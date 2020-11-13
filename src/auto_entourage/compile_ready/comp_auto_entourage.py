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

from ghpythonlib.componentbase import dotnetcompiledcomponent as component
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
import subprocess

class AutoEntourage(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "AutoEntourage", "AE", """Populates a given region (or ahcnor points) with entourages""", "Display", "Preview")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("8da439f7-c91d-4951-bef8-9a521b1d5add")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "path", "path", "File path to the image folder.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "imgHeight", "imgHeight", "The entourage height in the model.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Point()
        self.SetUpParam(p, "point", "point", "The points where the entourage is anchored.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "layerName", "layerName", "Default to \"Entourage\" if not speficied.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Integer()
        self.SetUpParam(p, "seed", "seed", "(Optional) Sets random seed. ")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "load", "load", "Loads entourages in a new layer.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "orient", "orient", "(Re)orients the entourages to camera angle.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        pass    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        p4 = self.marshal.GetInput(DA, 4)
        p5 = self.marshal.GetInput(DA, 5)
        p6 = self.marshal.GetInput(DA, 6)
        result = self.RunScript(p0, p1, p2, p3, p4, p5, p6)

        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAKUSURBVEhLYyAF9EycaNXeN62tpKrFACpEPaBlH8oTnlL6obFnxv+yutb79fX1LFAp6gFNu/iLlv4F/51Dsw9AhSgHx48fF39486bShQsXFFt75zgm5HU01nfMtDp16pTSw4cPlW7cOCMCVUoe2LZzz7I7t2//OXP69J9LF85/vnntyotL5899AfHv3rnzZ9eeA5OgSskDs+evXP3g/v3/F86fx8Ag8VnzV06DKiUP1HdMX3H71q3/Z8+cQcHngPjmzZv/a9qmToEqJQ+kF7evuHb1+v9zZ8+iWHD+3Nn/ly5f/Z+Q10SZBQHx5SvOnrv4/8K5cygWXDx/7v/JU+f+e0UXU2aBfUD2ikNHT/0HRjCKBZcvXvi/58Cx/xbe6ZRZYOCStGL77kP/gakH6OrzcHzr+tX/G7bs/a9tH0eZBVq2savmLd30H5gs/x8+fBSOQb6YvmDdf1WrqKlQpeQBU/fUebYB2S+cQgr+OwTl/ncMzgPTTiH5/238c54buyf3Q5WSB8y8UgsNXJMmm3pl/TdyS/5v6Jr0C0SbemYC2cndph5puVClpANggcZk6p6ibeqZGmXll/cfaNgfU4/UfeZe6f8tfXOAlqT4mHsk60GVkwUYQYSZe4qtpW820MC070ALqkEWmHtl/DfxTtIBq6IUGHmkKoMMBRr+DhhkjmaeqX/NPFK/GvukUVbQwYCWfRYP0NAvwCB6YOGWLARkfwbiRwyhocxQJZQDkOFAV58GsYGGP4SxqQaA4X8caPAmdDbVgJln2iozz3Rw2W/mkbYSmLooy2DoABjBrUCDC0BsYPA0A3EJWIJaAJh6Yk09M3wg7PRIoI8CwBLUAuYemXrm3umqIDYo/Ru7pWmAJfACBgYAZcl3C7weA6kAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    
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

import GhPython
import System

class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "AutoEntourage"
    
    def get_AssemblyDescription(self):
        return """"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return ""
    
    def get_Id(self):
        return System.Guid("cbb49573-9fd7-4d64-a17e-3a8b9a040dad")
        
class ImgCrop(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ImgCrop", "Crop", """Crops white spaces from PNG images.""", "Display", "Preview")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("dc3e01bd-bdb2-459d-9590-bae40cdbd882")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = GhPython.Assemblies.MarshalParam()
        self.SetUpParam(p, "path", "path", "The path of the input directory")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = GhPython.Assemblies.MarshalParam()
        self.SetUpParam(p, "out", "out", "The path of the output directory")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = GhPython.Assemblies.MarshalParam()
        self.SetUpParam(p, "crop", "crop", "Script variable Python")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "status", "status", "Returns the status of execution.")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)
        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAANFSURBVEhLrVZJa1NRFO6PceHOjRtB3ehWKwhqwQER1IVbrSJYFyKIGNwIVVFqpaYxbeakSZomTZM2yXt5L3Py2gxtOlo6odXa0NLPc294kbZRg03g49z7cs/57nTOd1tEOdM6KsQ12j6zptdg1fSZ7YSBA8BOcVgssyYSTWla5KTyZvXbFuLpPPxjUTiHAoQRuH2jcA8TmP0X+LggBsjP5Q0gEJaRzBaxtr4NIhjXTM0sI5EuIJacwGg4Bod7GHqTHTqDlds+s+OPUMex9oBnBCEhgXgqTyhgcnqpSsAacmKco/pnHmExyVfTT469/RZ80pt5IJPdtatvsDr5KiLRNJ8k81Vj1SVQwQYyB+boC0SIUMZwMIRurR7BkEAzlfl3Uc5WAyd/B1bxVwIV0biC4uQc2O+zZQhHT1+igDnez02UIcXr+zE0RCDGclAmplCpVJDKFdDx/B2mZxd4P50rIRpT6voxNEQQo6WzgxMEAZl0ElPFPFKJBERBhChl+MWo58fQEEEyU6DDDsPr8yMmSYiKImKyhCGvn85Aou3av/cqGiJIZ0sw2Pyw2N1IxmOQolFaQRwmq4uuZZgmUKzrx9AQQVaZhNbgQY/OhBxtEZt9LpNCV48BZmcQKUqoen4MDRN80DmhedUFJZuGTNukEMGzl+9hdARohU0g6LcN4/yNhzh79R7OXLmL1mvtaLv9GE5v5OAELIkEKYsXnTocOtaGE+fu4PDxy3jbY6UkzBz8kFkezC8sUQFL4Mip63jw9DW3WcqNEiXggfOAEczMLUIplHGSZq81erhdXFpFvjjTHILJ8jwWFldw8VYHRCodF24+wsbPTZ7hTSEolGax/n0D9590Yu7LMtrJ7uzsIEMXoCkEE4VpbG1vo1vvwo+NTXzsc/Fi15RaJBHyxVkecLw4vctmx8s05j9rUYIUiWnCGBU6tzcI78gYhy8QqrUHSWjCYqomUntj7CNglVGVziBJp93lq0millSMHgW7bFUq7XAM+jEWiddESl1VjUDVZDmhwB8UYRnw4LPRxrFXg+tBZ7TysTanF4GQxIOzeCxui0SviuW1CilXDt5AmL8MnPQy2PdyaADqi8QXFEATx8rXCn4BRNZ/ilsLBDYAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    
    def __init__(self):
        component.__init__(self)
        self.status = ""
        self.prevInput = None
    
    def RunScript(self, path, out, crop):
        # replace guid with compiled guid of the auto_entourage component
        guid = System.Guid("8da439f7-c91d-4951-bef8-9a521b1d5add")
        auto_entourage = Grasshopper.Instances.ComponentServer.FindAssemblyByObject(guid)
        img_crop = auto_entourage.Location.replace("auto_entourage.ghpy",
                                                     "img_crop.exe")
        
        def runImgCrop():
            """Calls img_crop.exe and returns execution status.
            """
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            pipe = subprocess.Popen([img_crop, path, out], 
                                    startupinfo=startupinfo)
            pipe.communicate()
            
            return pipe.returncode
        
        def getWarningMessage():
            """Returns warning messages or None if no warnings found
            """
            message = None
            if not path or not out:
                message = "Both path and out needs to be specified"
            return message
            
        def displayWarnings():
            warning_message = getWarningMessage()
            if warning_message is not None:
                w = ghk.GH_RuntimeMessageLevel.Warning
                self.AddRuntimeMessage(w, warning_message)
        
        displayWarnings()
        
        if path and out:
            curInput = hash((path, out))
            if curInput != self.prevInput:
                self.status = "ImaCrop hasn't been run."
                self.prevInput = curInput
        
        if crop:
            if runImgCrop() == 0:
                self.status = "Cropped {} (out of {}) images and saved to {}".format(
                    len(os.listdir(out)), len(os.listdir(path)), out)
            else:
                self.status = "Unsuccessful. Nothing is saved."
            
        status = self.status
        return status


import GhPython
import System

class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "ImgCrop"
    
    def get_AssemblyDescription(self):
        return """"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return ""
    
    def get_Id(self):
        return System.Guid("d1b455c3-54cf-4fae-a1c2-85d32cdbb24c")