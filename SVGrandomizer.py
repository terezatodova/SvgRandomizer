import xml.etree.ElementTree as ET
import random
from svglib.svglib import svg2rlg
from numpy import interp

width = 100
height = 100
imageSimiliarity = 0.5 # If 0 the image will be very randomized, if 1 it will be slightly randomized 
imagePickProbability = 0.7 # What is the probability of modifying an object (1 = all objects will be modified, 0 = none will be modified)

def loadWidthAndHeight(inputFile):
    drawing = svg2rlg(inputFile)
    left, bottom, right, top = drawing.getBounds()
    width = right - left
    height = top - bottom
    return width, height

# based on imagePickProbability calculate whether to skip this object
def pickObject():
    random_number = random.uniform(0, 1)
    return random_number <= imagePickProbability

def changePosition(element, key, modification, dimension):
    newKey = float(element.get(key)) + random.uniform(-modification, modification)
    newKey = interp(newKey, [-modification, dimension + modification], [0, dimension])
    element.set(key, str(newKey))


def changeSize(element, key, modification, dimension):
    newSize = float(element.get(key)) * random.uniform(1 - modification, 1 + modification)
    newSize = interp(newSize, [0, dimension], [0, dimension])
    element.set(key, str(newSize))

# Randomize the position of the objects
# Keep the shape in bounds
def positionRandomize(element):
    xModification = width * (1 - imageSimiliarity)
    yModification = height * (1 - imageSimiliarity)
    
    # Check if the element is the one we want to modify
    if 'circle' in element.tag or 'ellipse' in element.tag:
        changePosition(element, 'cx', xModification, width)
        changePosition(element, 'cy', yModification, height)

    elif 'rect' in element.tag:
        changePosition(element, 'x', xModification, width)
        changePosition(element, 'y', yModification, height)

    elif 'polygon' in element.tag or 'path' in element.tag:
        translateX = random.uniform(-xModification, xModification)
        translateY = random.uniform(-yModification, yModification)
        element.set('transform', f"translate({translateX}, {translateY})")

# Randomize the size of the objects
def resize(element):
    newSize = random.uniform(0.5, 2.5)

    if 'transform' in element.attrib:
        element.set('transform', f"{element.get('transform')} scale({newSize}, {newSize})")
    else:
        element.set('transform', f"scale({newSize}, {newSize})")

# Randomize the rotation of the objects
def rotationRandomize(element):
    rotation = random.uniform(0, 360)
    if 'transform' in element.attrib:
        element.set('transform', f"{element.get('transform')} rotate({rotation})")
    else:
        element.set('transform', f"rotate({rotation})")

def DoNotModifyElement(element):
    # Check if a rectangle spans the entire image
    if 'rect' in element.tag:
        x = float(element.get('x', 0)) - 10
        y = float(element.get('y', 0)) - 10
        currWidth = float(element.get('width', 0)) + 10
        currHeight = float(element.get('height', 0)) + 10

        #return x <= 0 and y <= 0 and currWidth >= width and currHeight >= height
        return True
        
    elementTypes = ['circle', 'ellipse', 'rect', 'polygon', 'path']

    for elementType in elementTypes:
        if elementType in element.tag:
            return False

    return True


def createSVGFile(inputFile, outputFile, inImagePickProbability, inImageSimiliarity, modifyPosition, modifyRotation, modifySize):
    global imagePickProbability 
    imagePickProbability = inImagePickProbability
    global imageSimiliarity
    imageSimiliarity = inImageSimiliarity
    tree = ET.parse(inputFile)
    svgRoot = tree.getroot()
    global width
    global height
    width, height = loadWidthAndHeight(inputFile)

    
    for element in svgRoot.iter():
        if (DoNotModifyElement(element)):
            continue
    
        if not pickObject():
            continue

        # pick for position change
        if pickObject() and modifyPosition:
            positionRandomize(element)
        # pick for resize
        if pickObject() and modifySize:
            resize(element)
        # pick for rotation
        if pickObject() and modifyRotation:
            rotationRandomize(element)

    tree.write(outputFile)