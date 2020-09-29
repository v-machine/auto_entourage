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

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import Rhino.RhinoDoc
import ghpythonlib.components as ghc
import Grasshopper.Kernel as ghk
import random
import System
import math
import os
import inspect
        
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
    """Alternative method. Adds a vertical picture frame without using alpha
    """
    centering_vector = rs.VectorRotate(normal, 90, [0, 0, 1])
    point -= 0.5*centering_vector*width
    x_axis = rs.VectorRotate(normal, 90, [0, 0, 1])
    y_axis = rg.Vector3d(0, 0, 1)
    plane = rg.Plane(point, x_axis, y_axis)
    sc.doc.ActiveDoc.Objects.AddPictureFrame(plane, path, False, width, height,
                                                False, False)
    
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
    """Alternative method for loading picture frames
    """
    for idx, pt in enumerate(ptsList):
        img = imgList[idx % len(imgList)]
        height = img_height[idx % len(img_height)]
        try:
            width, height = scaleImage(*getImageSize(img), 
                                        targetHeight = height)
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
        placeImage(imgList, point, cameraDirection)

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

def warning_message():
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

def error_message():
    """Returns error messages or None if no errors found
    """
    message = None
    if region and region[0] is None:
        message = "region contains null values"
    if point and point[0] is None:
        message = "point contains null values"
    return message

deleteLayer(layer_name)
if place:
    populate(path, region, point, num)
else:
    deleteLayer(layer_name)
