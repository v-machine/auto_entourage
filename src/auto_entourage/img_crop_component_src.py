"""Crops white spaces from PNG images.
    Inputs:
        in_path: The path of the input directory
        out_path: The path of the output directory
    Output:
        status: Returns the status of execution.
"""
__author__ = "Vincent Mai"
__version__ = "2020.09.27"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import Grasshopper.Kernel as ghk
import System
import Rhino
import subprocess

class QuickCrop(component):
    
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
