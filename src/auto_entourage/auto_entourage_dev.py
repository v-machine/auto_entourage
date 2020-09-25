"""Populates a scene with .png entourages given 2D region(s) or anchor point(s)
"""
__author__ = "Vincent Mai"
__version__ = "0.1.0"

import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import Rhino.RhinoDoc as rhDoc
import ghpythonlib.components as ghc
import random
import System
import math
import os

PERSON_HEIGHT = 5.8
RANDOM_SEED = 0

def addPictureFrame(path, point, vector):
    """Returns a vertical picture frame, given a point (Rhino.Geometry.Point3d) and a vector (Rhino.Geometry.Vector)
    """
    path = chr(34) + path + chr(34)
    point -= vector/2
    vector += point
    cmd = cmd = "_-Pictureframe " + path + " " + "Vertical" + " " + str(point) + " " + str(vector) + " _EnterEnd"
    rs.Command(cmd, True)

def getFiles(path):
    """Returns a list of paths from a directory
    """
    fileList = os.listdir(path)
    return [path + file for file in fileList if file.endswith(".png")]

def getImageSize(path):
    """Returns the height and width of the image from the file path
    """
    bmp = System.Drawing.Bitmap.FromFile(path)
    return (bmp.Width, bmp.Height)

def createVector(baseVector, targetHeight, imgWidth, imgHeight):
    """Returns a x-axis vector that scales the input image to target height
    """
    factor = targetHeight/imgHeight
    return baseVector*imgWidth*factor

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
    region = rg.Brep.CreatePlanarBreps(region)
    return ghc.PopulateGeometry(region, num, seed=RANDOM_SEED)
    
def placeImage(imgList, ptsList, baseVector):
    for idx, pt in enumerate(ptsList):
        img = imgList[idx % len(imgList)]
        try:
            width, height = getImageSize(img)
            vector = createVector(baseVector, PERSON_HEIGHT, width, height)
            addPictureFrame(img, pt, vector)
        except:
            print("failed to process "+img)
    
def populate(path, region, point, num):
    """Populate a region (closed curve) with vertical picture frames
    """
    imgList = getFiles(path)
    baseVector = rs.VectorRotate(getCameraDirection(), 90, [0, 0, 1])
    if region:
        ptsList = populateRegion(region, num)
        placeImage(imgList, ptsList, baseVector)
    if point:
        placeImage(imgList, point, baseVector)

if not layer: layer = "entourage"
 
if run:
    sc.doc = rhDoc.ActiveDoc
    layer_idx = sc.doc.Layers.Add(layer, System.Drawing.Color.Black)
    sc.doc.Layers.SetCurrentLayerIndex(layer_idx, True)
    populate(path, region, point, num)
    sc.doc.Layers.SetCurrentLayerIndex(0, True)
else:
    sc.doc = rhDoc.ActiveDoc
    rhobjs = sc.doc.Objects.FindByLayer(layer)
    if rhobjs:
        for obj in rhobjs:
            sc.doc.Objects.Delete(obj)
    sc.doc.Layers.SetCurrentLayerIndex(0, True)
    sc.doc.Layers.Delete(sc.doc.Layers.FindName(layer), True)