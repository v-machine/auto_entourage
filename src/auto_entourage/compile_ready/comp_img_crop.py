"""Crops white spaces from PNG images.
    Inputs:
        path: The path of the input directory
        out: The path of the output directory
    Output:
        status: Returns the status of execution.
"""
__author__ = "Vincent Mai"
__version__ = "2020.09.27"

from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import Grasshopper.Kernel as ghk
import System
import os
import Rhino
import subprocess

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