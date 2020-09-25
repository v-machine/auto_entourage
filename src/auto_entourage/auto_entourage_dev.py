import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import ghpythonlib.components as ghc
import random
import System
import math
import os


PERSON_HEIGHT = 5.8

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
    
def populate(path, region, num):
    """Populate a region (closed curve) with vertical picture frames
    """
    fileList = getFiles(path)
    ptsList = ghc.Populate2D(region, num, seed=1)
    baseVector = rs.VectorRotate(getCameraDirection(), 90, [0, 0, 1])
    
    for idx, pt in enumerate(ptsList):
        img = fileList[idx % len(fileList)]
        try:
            width, height = getImageSize(img)
            vector = createVector(baseVector, PERSON_HEIGHT, width, height)
            addPictureFrame(img, pt, vector)
        except:
            print("can't process "+img)
    
def debug():
    pass

debug()
if run:
   populate(path, region, num)        