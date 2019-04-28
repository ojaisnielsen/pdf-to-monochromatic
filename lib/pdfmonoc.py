# coding=UTF-8
from PIL import Image
import sys
import os
import numpy
import ConfigParser

def progExists(prog):
    exists = False
    for dirPath in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(dirPath, prog)):
            exists = True
    return exists

def emptyDir(dirPath): 
    fileList = os.listdir(dirPath)
    for fileName in fileList:
        os.remove(os.path.join(dirPath, fileName))

dataDir = os.path.dirname(os.path.abspath(sys.argv[0]))
tempDir = os.path.join(dataDir, "Temp")
colors = ["rouge", "vert", "bleu", "noir"]
configFile = os.path.join(dataDir, "config.ini")
gsPath = ""
convertPath = ""
defaultColor = ""
if os.path.exists(configFile):
    defaultValues = ConfigParser.ConfigParser()
    defaultValues.read([configFile])
    if defaultValues.has_option("Programs", "GhostScript"):
        gsPath = defaultValues.get("Programs", "GhostScript")
    if defaultValues.has_option("Programs", "ImageMagick"):
        convertPath = defaultValues.get("Programs", "ImageMagick")
    if defaultValues.has_option("Parameters", "DefaultColor"):
        defaultColor = defaultValues.get("Parameters", "DefaultColor")

if os.path.exists(os.path.join(gsPath, "gs")):
    gsCommand = "gs"
elif os.path.exists(os.path.join(gsPath, "gswin32c.exe")):
    gsCommand = "gswin32c.exe"   
elif progExists("gs"):
    gsCommand = "gs"
    gsPath = ""
elif progExists("gswin32c.exe"):
    gsCommand = "gswin32c.exe"
    gsPath = ""
else:
    print u"Veuillez installer GhostScript dans votre PATH ou renseigner le chemin d'accés dans le fichier \"config.ini\"."
    exit()

if os.path.exists(os.path.join(convertPath, "convert")):
    convertCommand =  "convert"
elif os.path.exists(os.path.join(convertPath, "convert.exe")):
    convertCommand = "convert.exe"
elif progExists("convert"):
    convertCommand = "convert"
    convertPath = ""
elif progExists("convert.exe"):
    convertCommand = "convert.exe"
    convertPath = ""
else:
    print u"Veuillez installer ImageMagick dans votre PATH ou renseigner le chemin d'accés dans le fichier \"config.ini\"."
    exit()

if len(sys.argv) == 1:
    print u"Veuillez indiquer un fichier PDF"
    exit()

pdfFile = os.path.abspath(sys.argv[1])
pdfFileName, pdfFileExt = os.path.splitext(pdfFile)

if pdfFileExt.lower() != ".pdf" or not(os.path.exists(pdfFile)):
    print u"Veuillez indiquer un fichier PDF valide"
    exit()

if len(sys.argv) > 2 and sys.argv[2].lower() in colors:
    colorId = colors.index(sys.argv[2].lower())
elif defaultColor in colors:
    colorId = colors.index(defaultColor)
else:
    colorId = 3

if os.path.isdir(tempDir):
    emptyDir(tempDir)
else:
    os.mkdir(tempDir)



print "Conversion du PDF en images... "
if (gsPath != ""):
    os.chdir(gsPath)
gsCompute = os.popen("%s -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 -dTextAlphaBits=4 -sOutputFile=\"%s\" \"%s\"" % (gsCommand, os.path.join(tempDir, "%00d.png"), pdfFile))
gsCompute.read()
tempFiles = os.listdir(tempDir)
if len(tempFiles) == 0:
    print u"Veuillez indiquer un fichier PDF valide"
    exit()
print u"Terminé\n"
        
print "Conversion des images en %s... " % colors[colorId]
os.chdir(tempDir)
for tempFile in tempFiles:
    image = Image.open(tempFile)
    image = image.convert("RGB")
    R, G, B = image.split()
    R = numpy.array(R.getdata())
    G = numpy.array(G.getdata())
    B = numpy.array(B.getdata())
    grayScale = 0.3*R + 0.59*G + 0.11*B
    monocBand = Image.new("L", image.size)
    monocBand.putdata(grayScale)
    whiteBand = Image.new("L", image.size, 255)
    if colorId == 0: 
        monocImage = Image.merge("RGB",(whiteBand, monocBand, monocBand))
    if colorId == 1: 
        monocImage = Image.merge("RGB",(monocBand, whiteBand, monocBand))
    if colorId == 2: 
        monocImage = Image.merge("RGB",(monocBand, monocBand, whiteBand))
    if colorId == 3: 
        monocImage = monocBand
    monocImage.save(os.path.abspath(tempFile))
print u"Terminé\n"

print "Conversion des images en PDF... "
if (convertPath != ""):
    os.chdir(convertPath)
convertCompute = os.popen("%s \"%s\" \"%s_monochrome.pdf\"" % (convertCommand, os.path.join(tempDir, "*.png"), pdfFileName))
convertCompute.read()
print u"Terminé\n"

print "Suppression des fichiers temporaires... "
emptyDir(tempDir)
print u"Terminé\n"


