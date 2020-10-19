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

import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import ghpythonlib.components as ghc
import Grasshopper.Kernel as ghk
import random
import os
from ghutil import RhinoDocContext, NewLayerContext, TreeHandler

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
def populateRegion(region, num):
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
def loadImage(path, num):
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

def populate(path, img_height, region, point, num):
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
            pts = populateRegion(region, num)
            imgs = loadImage(path, num)
            placeImage(imgs, pts, cameraDirection, img_height)
        if point.AllData():
            num = TreeHandler.topologyTree(point)
            imgs = loadImage(path, num)
            placeImage(imgs, point, cameraDirection, img_height)
       
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
    if len(layer_name) > 1:
        message = "Multiple layer names not supported"
    return message

:q
layer_name = layer_name.AllData()       
if not layer_name: 
    layer_name = "Entourage"
else:
    layer_name = layer_name[0]
if not seed:
    seed = RANDOM_SEED

if place:
    populate(path, img_height, region, point, num)
