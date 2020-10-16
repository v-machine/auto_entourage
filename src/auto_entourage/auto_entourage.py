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

import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import Rhino.RhinoDoc
import ghpythonlib.components as ghc
import ghpythonlib.treehelpers as th
import Grasshopper.Kernel as ghk
import random
import math
import os
import inspect
from treehandler import TreeHandler

RANDOM_SEED = 0
ghdoc = sc.doc

random.seed(RANDOM_SEED)
        
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
    """Calls rhinoscriptsyntax's addPictureFrame method and centers the
    picture around the given point
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

@TreeHandler
def populateRegion(region, num):
    """Returns a list of populated points given a region
    """
    brep = rg.Brep.CreatePlanarBreps(region)
    return ghc.PopulateGeometry(brep, num, seed=RANDOM_SEED)

@TreeHandler
def placeImage(img, pt, normal, img_height):
    """Places images given an list of anchor points and normal vector
    """
    try:
        width, height = scaleImage(*getImageSize(img),
                                    targetHeight=img_height)
        addPictureFrame(img, pt, normal, width, height)
    except:
        print("Failed to process {}".format(img))
                    
def inNewLayer(layer_name):
    """Decorator to call a function in a new layer
    """
    def wrap_func(func):
        def wrapper(*args, **kwargs):
            createAndSetCurrentLayer(layer_name)
            func(*args, **kwargs)
            resetLayer()
        return wrapper
    return wrap_func

@TreeHandler
def getImages(path, num):
    """Randomly choose a number of images from the given file path
    """
    imgList = getFiles(path)
    return [imgList[i % len(imgList)] for i in range(num)]

@inNewLayer(layer_name)
def populate(path, img_height, region, point, num):
    """Populate a region (closed curve) with vertical picture frames
    """
    cameraDirection = th.list_to_tree([getCameraDirection()])
    if region.AllData():
        pts = populateRegion(region, num)
        imgs = getImages(path, num)
        placeImage(imgs, pts, cameraDirection, img_height)
    if point.AllData():
        num = TreeHandler.branchDataSize(point)
        imgs = getImages(path, num)
        placeImage(imgs, point, cameraDirection, img_height)
        
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
        
deleteLayer(layer_name)
        
if place:
    populate(path, img_height, region, point, num)
else:
    deleteLayer(layer_name)