"""Populates a given region (or ahcnor points) with entourages
    Inputs:
        path: File path to the image folder.
        img_height: The entourage height in the model.
        region: A region delineated by a closed curve.
        num: The number of entourages within the region.
        point: (Optional) The points where the entourage is anchored.
        layer_name: Default to "Entourage" if not speficied.
        seed: (Optional) Sets random seed. 
        place: Loads entourages in a new layer.
"""
__author__ = "Vincent Mai"
__version__ = "0.1.0"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import ghpythonlib.components as ghc
import Grasshopper.Kernel as ghk
import random
import os
import Rhino.RhinoDoc
from Grasshopper import DataTree
import ghpythonlib.treehelpers as th

class AutoEntourage(component):
    
    def RunScript(self, path, img_height, region, num, point, layer_name, seed, place):
        
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
            def topologyTree(tree):
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
        
        
        RANDOM_SEED = 0
        UNIT_Z = (0, 0, 1)
        
        def addPictureFrame(path, point, normal, width, height):
            """Calls rhinoscriptsyntax's addPictureFrame method 
            
            Creates a picture frame in Rhino and centers it around a given point. The 
            picture frame will always be vertical and are not cached in grasshopper.
            
            Args:
                path (str): path to .png image
                point (rg.Point3d): anchor for picture frame
                normal (rg.Vector3d): xy-orientation of the picture frame
                width (float): width of the picture frame
                height (float): height of the picture fram
            """
            with RhinoDocContext():
                x_axis = rs.VectorRotate(normal, 90, UNIT_Z)
                y_axis = rg.Vector3d(*UNIT_Z)
                point -= 0.5*x_axis*width
                plane = rg.Plane(point, x_axis, y_axis)
                sc.doc.ActiveDoc.Objects.AddPictureFrame(plane, path, False, width, 
                                                         height, False, False)
                    
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
                targetHeight (float): the target height to scale to
            Returns:
                the scaled (width, height)
            """
            factor = targetHeight / baseHeight
            return baseWidth*factor, targetHeight
                    
        def getCameraDirection():
            """Returns the camera direction of the active viewport
            """
            cameraDir = sc.doc.Views.ActiveView.ActiveViewport.CameraDirection
            projCameraDir = rg.Vector3d(cameraDir.X, cameraDir.Y, 0)
            projCameraDir.Unitize()
            return projCameraDir
        
        @TreeHandler
        def populateRegion(region, num, seed):
            """Returns a list of populated points given a region
            
            Args:
                region (rg.Curve): a closed-curve delimiting a region
                num (int): the number of points to populate the region
            Returns:
                a list of 3d points
            """
            brep = rg.Brep.CreatePlanarBreps(region)
            return ghc.PopulateGeometry(brep, num, seed=seed)
        
        @TreeHandler
        def placeImage(path, pt, normal, img_height):
            """Orients, scales, and places the input image as a PictureFrame
            
            Orients the input image based on normal, scales it to the target height 
            and centers it on the input point.
           
            Args:
                img(str): path to the .png image 
                pt (rg.Point3d): the anchor to center the PictureFrame
                normal (rg.Vector3d): the normal vector of the PictureFrame
                img_height (float): the target height to scale to
            Notes:
                Skips images should they failed to be added to Rhino document
            """
            try:
                width, height = scaleImage(*imageSize(path), targetHeight=img_height)
                addPictureFrame(path, pt, normal, width, height)
            except:
                print("Failed to process {}".format(path))
                            
                
        @TreeHandler
        def loadImage(path, num, seed):
            """Randomly choose a number of images from the given file path
            
            Args:
                path (str): path to the directory contain the .png images
                num (int): the number of images to load randomly
            Returns:
                a list of images loaded from the given directory
            """
            random.seed(seed)
            imgList = getFiles(path)
            imgList = random.sample(imgList, len(imgList))
            return [imgList[i % len(imgList)] for i in range(num)]
        
        def populate(path, img_height, region, point, num, seed):
            """Populate a region (closed curve) with vertical PictureFrames
            
            Args:
                path (str): path to the directory of .png images 
                img_height (float: the target height of the picture frame
                region (rg.Curve): a closed curve
                point (rg.Point3d): the anchor point of the picture frame
                num (int): the num of PictureFrames to populate a region
            """
            with NewLayerContext(layer_name):
                cameraDirection = getCameraDirection()
                if region.AllData():
                    pts = populateRegion(region, num, seed)
                    imgs = loadImage(path, num, seed)
                    placeImage(imgs, pts, cameraDirection, img_height)
                if point.AllData():
                    num = TreeHandler.topologyTree(point)
                    imgs = loadImage(path, num, seed)
                    placeImage(imgs, point, cameraDirection, img_height)
               
        def get_warning_message():
            """Returns warning messages or None if no warnings found
            """
            message = None
            if not path.AllData():
                message = "Path to PNGs is missing"
            elif not img_height.AllData():
                message = "img_height is missing"
            elif not point.AllData() and not region.AllData():
                message = "At least one region or one point is needed"
            if region.AllData() and not num.AllData():
                message = "Please specify num (of entourages) in region"
            return message
        
        def get_error_message():
            """Returns error messages or None if no errors found
            """
            message = None
            if len(layer_name.AllData()) > 1:
                message = "Multiple layer names not supported"
            return message
        
        def display_warnings():
            warning_message = get_warning_message()
            if warning_message is not None:
                w = ghk.GH_RuntimeMessageLevel.Warning
                self.AddRuntimeMessage(w, warning_message)
        
        def display_errors():
            error_message = get_error_message()
            if error_message is not None:
                e = ghk.GH_RuntimeMessageLevel.Error
                self.AddRuntimeMessage(e, error_message)
                
        display_warnings()
        display_errors()

        if not layer_name.AllData(): 
            layer_name = "Entourage"
        else:
            layer_name = layer_name.AllData()[0]
            
        if seed.BranchCount == 0:
            seed = RANDOM_SEED
            
        if place:
            populate(path, img_height, region, point, num, seed)