"""Populates a given region (or ahcnor points) with entourages
    Inputs:
        path: File path to the image folder.
        img_height: The entourage height in the model.
        region: A region delineated by a closed curve.
        num: The number of entourages within the region.
        point: (Optional) The points where the entourage is anchored.
        layer_name: Default to "Entourages" if not speficied.
        place: If true, loads entourages in a new layer; if false, deletes entourages and the new layer.
"""
__author__ = "Vincent Mai"
__version__ = "0.1.0"

from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import Rhino.RhinoDoc
import ghpythonlib.components as ghc
import Grasshopper.Kernel as ghk
import random
import math
import os
import inspect
import subprocess

class AutoEntourage(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Auto Entourage", "AutoEnto", """Populates a given region (or ahcnor points) with entourages""", "Display", "Preview")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("9e1aaf9a-3496-42b2-a827-c9ae515b3226")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "path", "path", "File path to the image folder.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "img_height", "img_height", "The entourage height in the model.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "region", "region", "A region delineated by a closed curve.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Integer()
        self.SetUpParam(p, "num", "num", "The number of entourages within the region.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Point()
        self.SetUpParam(p, "point", "point", "(Optional) The points where the entourage is anchored.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "layer_name", "layer_name", "Default to \"Entourages\" if not speficied.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "place", "place", "If true, loads entourages in a new layer; if false, deletes entourages and the new layer.")
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

    
    def RunScript(self, path, img_height, region, num, point, layer_name, place):
                
        RANDOM_SEED = 0
        ghdoc = sc.doc
        
        if not layer_name: 
            layer_name = "Entourages"
        
        def rhinoDocContext(func):
            """Decorator to switch ghdoc context to rhinodoc
            """
            def wrapper(*args, **kwargs):
                sc.doc = Rhino.RhinoDoc.ActiveDoc
                func(*args, **kwargs)
                sc.doc = ghdoc
            return wrapper
        
        @rhinoDocContext
        def addPictureFrame(path, point, normal, width, height):
            """Calls rhinoscriptsyntax's method of addPictureFrame and centers the
            picture around the given point
            """
            centering_vector = rs.VectorRotate(normal, 90, [0, 0, 1])
            point -= 0.5*centering_vector*width
            x_axis = rs.VectorRotate(normal, 90, [0, 0, 1])
            y_axis = rg.Vector3d(0, 0, 1)
            plane = rg.Plane(point, x_axis, y_axis)
            sc.doc.ActiveDoc.Objects.AddPictureFrame(plane, path, False, width,
                                                     height, False, False)
            
        def getFiles(path):
            """Returns a list of paths to PNGs from a directory
            """
            fileList = os.listdir(path)
            return [path + file for file in fileList if file.endswith(".png")]
        
        def getImageSize(path):
            """Returns the height and width of the image from the file path
            """
            bmp = System.Drawing.Bitmap.FromFile(path)
            return (bmp.Width, bmp.Height)
        
        def scaleImage(baseWidth, baseHeight, targetHeight):
            """scales image by the target height
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
        
        def populateRegion(region, num):
            """Returns a list of populated points given a region
            """
            brep = rg.Brep.CreatePlanarBreps(region)
            return ghc.PopulateGeometry(brep, num, seed=RANDOM_SEED)
        
        def placeImage(imgList, ptsList, normal):
            """Places images given an list of anchor points and normal vector
            """
            for idx, pt in enumerate(ptsList):
                img = imgList[idx % len(imgList)]
                try:
                    width, height = scaleImage(*getImageSize(img),
                                               targetHeight=img_height)
                    addPictureFrame(img, pt, normal, width, height)
                except:
                    print("Failed to process {}".format(img))
                    
        def inNewLayer(layer_name):
            """Decorator to call a function in a newly created layer
            """
            def wrap_func(func):
                def wrapper(*args, **kwargs):
                    createAndSetCurrentLayer(layer_name)
                    func(*args, **kwargs)
                    resetLayer()
                return wrapper
            return wrap_func
        
        @inNewLayer(layer_name)
        def populate(path, region, point, num):
            """Populate a region (closed curve) with vertical picture frames
            """
            imgList = getFiles(path)
            imgList = random.sample(imgList, len(imgList))
            cameraDirection = getCameraDirection()
            if region:
                ptsList = populateRegion(region, num)
                placeImage(imgList, ptsList, cameraDirection)
            if point:
                placeImage(imgList, [point], cameraDirection)
                
        
        @rhinoDocContext
        def createAndSetCurrentLayer(layer_name):
            """Creates a layer with the given name
            """
            layer = sc.doc.Layers.FindName(layer_name)
            if layer is None:
                layer_idx = sc.doc.Layers.Add(layer_name, System.Drawing.Color.Black)
            else:
                layer_idx = layer.Index
            sc.doc.Layers.SetCurrentLayerIndex(layer_idx, True)
        
        @rhinoDocContext
        def resetLayer():
            """Resets layer to default layer
            """
            sc.doc.Layers.SetCurrentLayerIndex(0, True)
        
        @rhinoDocContext
        def deleteLayer(layer_name):
            """Deletes a layer by its name as well as all objects inside
            """
            rhinoObjects = sc.doc.Objects.FindByLayer(layer_name)
            if rhinoObjects:
                for obj in rhinoObjects:
                    sc.doc.Objects.Delete(obj)
            sc.doc.Layers.SetCurrentLayerIndex(0, True)
            sc.doc.Layers.Delete(sc.doc.Layers.FindName(layer_name), True)
        
        def get_warning_message():
            """Returns warning messages or None if no warnings found
            """
            message = None
            if not path:
                message = "Path to PNGs is missing"
            elif not img_height:
                message = "img_height is missing"
            elif not point and not region:
                message = "At least one region or one point is needed"
            if region and not num:
                message = "Need to specify num (of entourages) in region"
            return message
        
        def get_error_message():
            """Returns error messages or None if no errors found
            """
            message = None
            if region and point:
                message = "choose region or point but not both"
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
        
        if place:
            populate(path, region, point, num)
        else:
            deleteLayer(layer_name)
            
class QuickCrop(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Quick Crop", "QCrop", """Crops white spaces from PNG images.""", "Display", "Preview")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("d7ce3cad-48f1-477b-a522-609b99a8e3f1")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = GhPython.Assemblies.MarshalParam()
        self.SetUpParam(p, "in_path", "in_path", "The path of the input directory")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = GhPython.Assemblies.MarshalParam()
        self.SetUpParam(p, "out_path", "out_path", "The path of the output directory")
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
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAANISURBVEhLrZZrTxNBGIX5SCDR/0Ci8ZOiaGJQo1EaqvFKNBHUIAENivFSgqBBAjEIgjZCEIWiXEWoQGsv9EqLtHS3ZXdbSgXKHS+f/A8cZ7aFgESJLG9yst1N9jz7zpnOTMzfyul0xjIjfKkQCFV5R4S14tfe70tKCsfFxeFPxcfHa6N264vjuO2Mj1+a//YT4Zl5TM0uiJpd+C5qem4RYXIfnlmgRpDJZJDL5StKTEykkKWo3fpiWXYbAfwKBL9iyOOFzmSD3jyAhuYOKOsa0KM1Qm+yw2IfFL+WmiYkJIAWvcbGxorPo3brazVg0M2Ihm1dGhy7cAspaTfx/FUDNAYzgdhWAKvrvwBfhhmoCaBPb8a9YiXOZRZB1aZGr64fBrNdWgd+2oGLgds9DIZhwfMcBJ6Hz+uDx8PARbqjRnTMqemy6DOijTMYDU2Q8XcQgAejfgF+gY+IQIIBP8w2J1JkqcuGa/TPWbQMCI2H0dljhNniIAA/eI5bUYAAO7p1cLOkq9EQ3F5+f/T1jWsZMD45haYODT71GRAKBtYAaBe1jZ3w+PjNAybCU6h/r4aqRY3xUHDFXCBZ0BzKqlVgOb8UwDRqVV2orm3G9OQ4AoIgio4/zUVR8gojwqh0gOKJEl/HgvCSr6aiM0lntCJH8QxCYEwaoKldg5RL93AqIx/ydAVSL0ckv/wAN/Mr4SfmkkJuVxuQV1SFPSeysFeWjf2pN7DryDWcv16ISjJ0XikZBMn/wGwfIrOlAwfkN3D0wh1czH4sAnIU5dCSYZIUMl0q3KwP7d1aJJ/Oxcn0fNwvfokdyRkkYCWcLrcYMk9y2DRgaJjFJ7IWHb94F2lZj1BR8w47D10hU/Qt7IMu6QC6mmqNFpy5VoCreaVobFVj9/EsKOtbYXV82RqAwWxDem4Jcgsq0dWrx+Gzt9HQ0k3yGdw6wK2Hz/GwrEbcB85lFqL1Yx/6rY6tAehNVhRXvEa5UgVdv1XspLPnM4yWAekAp8sjbi7KN62oa/oAjd6Epy8aCUBHlnK7NADdcFyMD/1k3dcabaKhye4ku5uFfL0DNucmZ1HkVMEtza06VdCTBBX9PTMfuUa0iLnFH3Cx3MHo69GKifkNHjn+HESnd6kAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    
    def RunScript(self, in_path, out_path, crop):
        
        status = None
        
        # replace guid with compiled guid of the auto_entourage component
        guid = System.Guid("9e1aaf9a-3496-42b2-a827-c9ae515b3226")
        auto_entourage = Grasshopper.Instances.ComponentServer.FindAssemblyByObject(guid)
        quick_crop = auto_entourage.Location.replace("auto_entourage.ghpy",
                                                     "quick_crop.exe")
        
        def call_quick_crop():
            """Calls quick_crop.exe and returns execution status.
            """
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            pipe = subprocess.Popen([quick_crop, in_path, out_path], 
                                    startupinfo=startupinfo)
            pipe.communicate()
            
            if pipe.returncode == 0:
                return "Cropping is successful. Saved to {}".format(out_path)
            else:
                return "Cropping is unsuccessful. Nothing is saved."
        
        def get_warning_message():
            """Returns warning messages or None if no warnings found
            """
            message = None
            if not in_path or not out_path:
                message = "Both in_path and out_path needs to be specified"
            return message
            
        def display_warnings():
            warning_message = get_warning_message()
            if warning_message is not None:
                w = ghk.GH_RuntimeMessageLevel.Warning
                self.AddRuntimeMessage(w, warning_message)
        
        display_warnings()
        
        if in_path and out_path and crop:
            status = call_quick_crop()
        
        return status

import GhPython
import System

class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "Auto Entourage"
    
    def get_AssemblyDescription(self):
        return """"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return ""
    
    def get_Id(self):
        return System.Guid("71e6952b-fc59-4ae3-ab93-dddfe01265a5")