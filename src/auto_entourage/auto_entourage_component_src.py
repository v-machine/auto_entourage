"""Populates a given region (or ahcnor points) with entourages
    Inputs:
        path: File path to the image folder.
        imgHeight: The entourage height in the model.
        point: The points where the entourage is anchored.
        layerName: Default to "Entourage" if not speficied.
        seed: (Optional) Sets random seed. 
        load: Loads entourages in a new layer.
        orient: (Re)orients the entourages to camera angle.
"""
__author__ = "Vincent Mai"
__version__ = "0.5.0"

from ghpythonlib.componentbase import executingcomponent as component
from Grasshopper import DataTree
import Grasshopper, GhPython
import Rhino
import Rhino.Geometry as rg
import Rhino.RhinoDoc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import ghpythonlib.components as ghc
import ghpythonlib.treehelpers as th
import Grasshopper.Kernel as ghk
import System
import math
import random
import os

class AutoEntourage(component):
    
    class Struct:
        """Cache the state of the loaded entourages
        """
        def __init__(self):
            self.pictureframeIds = None
            self.point = None
            self.cameraDir = None
        
        def cache(self, pictureframeIds=None, point=None, cameraDir=None):
            """Caches the current state of the loaded entourages
    
            Args:
                pictureframeIds (gh.DataTree): guid of pictureframe
                point (gh.DataTree): anchor points for pictureframes/entourages
                cameraDir (rg.Vector3d): the cameraDirection of active viewport
            """
            if pictureframeIds:
                self.pictureframeIds = pictureframeIds
            if point:
                self.point = point
            if cameraDir:
                self.cameraDir = cameraDir
    
        def clear(self):
            """clears all attributes"""
            for attr in self.__dict__:
                self.__dict__[attr] = None
                
    def __init__(self):
        component.__init__(self)
        self.data = AutoEntourage.Struct()
        
    def RunScript(self, path, imgHeight, point, layerName, seed, load, orient):
        
        RANDOM_SEED = 0
        DEFAULT_LAYER_NAME = "Entourage"
        UNIT_Z = (0, 0, 1)
        class RhinoDocContext:
            """Context Manager to enter the RhinoDoc.ActiveDoc Context
            """
            def __init__(self):
                self.ghdoc = sc.doc
                self.rhinodoc = Rhino.RhinoDoc.ActiveDoc
        
            def __enter__(self):
                sc.doc = self.rhinodoc
        
            def __exit__(self, type, value, traceback):
                sc.doc = self.ghdoc
        
        class NewLayerContext:
            """Context Manager to call a function in a new layer
            """
            def __init__(self, layer_name):
                self.layer_name = layer_name
        
            def __enter__(self):
                self.__deleteLayer(self.layer_name)
                self.__createAndSetCurrentLayer(self.layer_name)
        
            def __exit__(self, type, value, traceback):
                self.__resetLayer()
        
            def __createAndSetCurrentLayer(self, layer_name):
                """Creates a new layer and set it as the current layer
                """
                with RhinoDocContext():
                    layer = sc.doc.Layers.FindName(layer_name)
                    if layer is None:
                        layer_idx = sc.doc.Layers.Add(layer_name, System.Drawing.Color.Black)
                    else:
                        layer_idx = layer.Index
                    sc.doc.Layers.SetCurrentLayerIndex(layer_idx, True)
                    
            def __resetLayer(self):
                """Resets current layer to the default (first) layer
                """
                with RhinoDocContext():
                    sc.doc.Layers.SetCurrentLayerIndex(0, True)
                    
            def __deleteLayer(self, layer_name):
                """Deletes a layer and all objects inside
                """
                with RhinoDocContext():
                    rhinoObjects = sc.doc.Objects.FindByLayer(layer_name)
                    if rhinoObjects:
                        for obj in rhinoObjects:
                            sc.doc.Objects.Delete(obj)
                    sc.doc.Layers.SetCurrentLayerIndex(0, True)
                    sc.doc.Layers.Delete(sc.doc.Layers.FindName(layer_name), True)
        
        class TreeHandler:
            """Decorating class to handle trees as args for user define functions
            """
            def __init__(self, func):
                self.func = func
                
            def __call__(self, *args, **kwargs):
                args = map(TreeHandler.toTree, args)
                for arg in args:
                    arg.SimplifyPaths()
                depths = [self.__treeDepth(t) for t in args]
                trees = [th.tree_to_list(arg, lambda x: x) for arg in args]
                return th.list_to_tree(self.__ghtree_handler(trees, depths))
        
            def __treeDepth(self, t):
                """returns the depth of the gh tree"""
                path = t.Path(t.BranchCount-1)
                return len(str(path).split(";"))
        
            def __intertwine(self, trees):
                """intertwine two trees with equal depth
                """
                result = []
                for i in range(max([len(t) for t in trees])): 
                    items = [t[min(i, len(t)-1)] for t in trees]
                    if isinstance(items[0], list):
                        result.append(self.__intertwine(items))
                    else:
                        result.append(self.func(*items))
                return result
        
            def __ghtree_handler(self, trees, depths):
                """Returns appropriate GH Tree by explicit looping
                """
                max_depth = max(depths)
                for idx, d in enumerate(depths):
                    for j in range(max_depth-d):
                        trees[idx] = [trees[idx]]
                return self.__intertwine(trees)
            
            @staticmethod
            def toTree(arg):
                """Converts object to Grasshopper.DataTree
                """
                if isinstance(arg, DataTree[object]):
                    return arg
                else:
                    if not isinstance(arg, list):
                        return th.list_to_tree([arg])
                    else:
                        return th.list_to_tree(arg)
            
            @staticmethod
            def treeTopology(tree):
                """Returns the tree's topology in an equivalently structure
                    Example:
                        >>> branchDataSize([[a, b, c], [x, y]])
                        >>> tree {1; 1}
                """
                def __listBranchSize(tree):
                    if isinstance(tree, DataTree[object]):
                        tree.SimplifyPaths()
                        tree = th.tree_to_list(tree, lambda x: x) 
                    result = []
                    for b in tree:
                        if isinstance(b[0], list):
                            result.append(__listBranchSize(b))
                        result.append([len(b)])
                    return result
                return th.list_to_tree(__listBranchSize(tree))
        
        def addPictureFrame(path, point, orientation, width, height):
            """Calls rhinoscriptsyntax's addPictureFrame method, return objectID
            
            Creates a vertical picture frame in Rhino and centers it around the
            anchor point.
            
            Args:
                path (str): path to .png image
                point (rg.Point3d): anchor point for the picture frame
                orietation (rg.Vector3d): the orientation of the picture frame
                width (float): width of the picture frame
                height (float): height of the picture fram
            Returns:
                (RhinoObjects.Id) the guid of the pictureframe
            """
            with RhinoDocContext():
                xAxis = rs.VectorRotate(orientation, 90, UNIT_Z)
                yAxis = rg.Vector3d(*UNIT_Z)
                point -= 0.5*xAxis*width
                plane = rg.Plane(point, xAxis, yAxis)
                objId = sc.doc.ActiveDoc.Objects.AddPictureFrame(plane, path, False,
                                                                 width, height, False, False)
                return objId 
                
                    
        def getFiles(path):
            """Returns a list of paths to PNGs from a directory
            
            Args:
                path (str): the directory containing trimmed .png image
            Returns:
                list of absolute paths to .png files
            """
            fileList = os.listdir(path)
            return [path + file for file in fileList if file.endswith(".png")]
                
        def imageSize(path):
            """Returns the height and width of the image from the file path
            
            Args:
                path (str): the path to the .png file
            Returns:
                (width, height) of the .png
            """
            bmp = System.Drawing.Bitmap.FromFile(path)
            return (bmp.Width, bmp.Height)
                
        def scaleImage(baseWidth, baseHeight, targetHeight):
            """Scales the input width and height by the target height
            
            Args:
                baseWidth (float): the original width of the .png file
                baseHeight (float): the original height of the .png file
                targetHeight (float): the target height
            Returns:
                the scaled (width, height)
            """
            factor = targetHeight / baseHeight
            return baseWidth*factor, targetHeight
                    
        def getCameraDirection():
            """Returns the viewport camera direction (projected on XY plane)
        
            Returns:
                (rg.Vector3d) a vector representing the camera direction
            """
            cameraDir = sc.doc.Views.ActiveView.ActiveViewport.CameraDirection
            projCameraDir = rg.Vector3d(cameraDir.X, cameraDir.Y, 0)
            projCameraDir.Unitize()
            return projCameraDir
        
        @TreeHandler
        def placeImage(path, point, orientation, imgHeight):
            """Orients, scales, and places the input image as a PictureFrame
            
            Orients the input image based on orientation, scales it to the
            target height and centers it on the anchor point.
           
            Args:
                img(str): path to the .png image 
                point (rg.Point3d): the anchor to center the PictureFrame
                orientation (rg.Vector3d): the normal vector of the PictureFrame
                imgHeight (float): the target height to scale to
            Notes:
                Skips images should they failed to be added to Rhino document
            """
            try:
                width, height = scaleImage(*imageSize(path), targetHeight=imgHeight)
                return addPictureFrame(path, point, orientation, width, height)
            except:
                print("Failed to process {}".format(path))
                            
                
        @TreeHandler
        def loadImage(path, num, seed):
            """Randomly choose a number of images from the given file path
            
            Args:
                path (str): path to the image directory
                num (int): the number of images to load
                seed (int): random seed to randomize loading
            Returns:
                a list of images loaded from the given directory
            """
            random.seed(seed)
            imgList = getFiles(path)
            imgList = random.sample(imgList, len(imgList))
            return [imgList[i % len(imgList)] for i in range(num)]
        
        def populate(path, imgHeight, point, layerName, seed, data):
            """Populates a Rhino document with entourages (vertical PictureFrames)
            and caches the current state
            
            Args:
                path (str): path to the directory of .png images 
                imgHeight (float: the target height of the picture frame
                point (rg.Point3d): the anchor point of the picture frame
                seed (int): the random seed for loadImage and populateRegion
                data (EntourageData): the current state of the entourages
            """
            with NewLayerContext(layerName):
                cameraDirection = getCameraDirection()
                num = TreeHandler.treeTopology(point)
                imgs = loadImage(path, num, seed)
                pfIds = placeImage(imgs, point, cameraDirection, imgHeight)
                data.cache(pictureframeIds=pfIds, point=point,
                           cameraDir=cameraDirection)
        
        def orientImages(data):
            """(Re)orients existing entourages to a new camera angle and
            caches new cameraDir
        
            Args:
                data: the cache data of entourages
            """
            @TreeHandler
            def rotate(guid, center, angle):
                rs.RotateObject(guid, center, angle)
        
            with RhinoDocContext():
                rs.EnableRedraw(False)
                angle = orientAngle(data.cameraDir, getCameraDirection())
                rotate(data.pictureframeIds, data.point, angle)
                rs.EnableRedraw(True)
                data.cache(cameraDir=getCameraDirection())
            
        
        def orientAngle(v1, v2):
            """Returns the signed angle for orienting v1 to v2
        
            Args:
                v1 (rg.Vector3d): the base vector
                v2 (rg.Vector3d): the target vector
            """
            sign = lambda x: x and (1, -1)[x < 0]
            angle = rg.Vector3d.VectorAngle(v1, v2)
            cross = rg.Vector3d.CrossProduct(v1, v2)
            direction = sign(rg.Vector3d.Multiply(cross, rg.Vector3d(*UNIT_Z)))
            return direction * math.degrees(angle)
        
        def validInput():
            if (not path.AllData() or
                not imgHeight.AllData() or
                not point.AllData() or
                len(layerName.AllData()) > 1):
                return False
            return True
            
        def getWarningMessage():
            """Returns warning messages or None if no warnings found
            """
            message = None
            if not path.AllData():
                message = "Path to PNGs is missing"
            elif not imgHeight.AllData():
                message = "imgHeight is missing"
            elif not point.AllData():
                message = "At least one point is needed"
            return message
        
        def getErrorMessage():
            """Returns error messages or None if no errors found
            """
            message = None
            if len(layerName.AllData()) > 1:
                message = "Multiple layer names not supported"
            return message
            
        def displayWarnings():
            warning_message = getWarningMessage()
            if warning_message is not None:
                w = ghk.GH_RuntimeMessageLevel.Warning
                self.AddRuntimeMessage(w, warning_message)
        
        def displayErrors():
            error_message = getErrorMessage()
            if error_message is not None:
                e = ghk.GH_RuntimeMessageLevel.Error
                self.AddRuntimeMessage(e, error_message)
                
        displayWarnings()
        displayErrors()
        
        if layerName.BranchCount == 0: 
            layerName.Add(DEFAULT_LAYER_NAME)
        
        if seed.BranchCount == 0:
            seed.Add(RANDOM_SEED)
        
        if load and validInput():
            self.data.clear()
            populate(path, imgHeight, point, layerName.AllData()[0], seed, self.data)

        if orient:
            try:
                orientImages(self.data)
            except NameError:
                print("Entourages has not been loaded.")