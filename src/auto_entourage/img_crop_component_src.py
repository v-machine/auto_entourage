"""Crops white spaces from PNG images.
    Inputs:
        path: The path of the input directory
        out: The path of the output directory
    Output:
        status: Returns the status of execution.
"""
__author__ = "Vincent Mai"
__version__ = "2020.09.27"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import Grasshopper.Kernel as ghk
import System
import os
import Rhino
import subprocess

class ImgCrop(component):
    
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
