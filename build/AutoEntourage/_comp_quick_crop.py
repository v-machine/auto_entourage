"""Crops white spaces from PNG images.
    Inputs:
        in_path: The path of the input directory
        out_path: The path of the output directory
    Output:
        status: Returns the status of execution.
"""
__author__ = "Vincent Mai"
__version__ = "2020.09.27"

from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import Grasshopper.Kernel as ghk
import System
import Rhino
import subprocess

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
        return "Quick Crop"
    
    def get_AssemblyDescription(self):
        return """"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return ""
    
    def get_Id(self):
        return System.Guid("19c1356c-4c95-4e89-ae4e-472c43853b35")