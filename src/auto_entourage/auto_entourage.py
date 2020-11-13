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

import System
import math
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
        data (Struct): the current state of the entourages
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

if layerName.BranchCount == 0: 
    layerName.Add("Entourage")

if seed.BranchCount == 0:
    seed.Add(RANDOM_SEED)

if load and validInput():
    data = Struct()
    populate(path, imgHeight, point, layerName.AllData()[0], seed, data)

if orient:
    try:
        orientImages(data)
    except NameError:
        print("Entourages has not been loaded.")
