from flask import Flask, request, jsonify
from os import remove
from os.path import join as pjoin, exists, dirname, abspath
from zipfile import ZipFile
from cv2 import imread, dnn
from numpy import argmax

CDIR = dirname(abspath(__file__))
modelZip = pjoin(CDIR, 'model.zip')
modelDir = pjoin(CDIR, 'model')

def installModel():
    print('Model is not exists!\nDownloading... (230 MB)')
    from requests import get
    with open(modelZip, 'wb') as f:
        f.write(get('https://www.dropbox.com/s/bsb4qew5h0mvm1l/model.zip?dl=1').content)
    with ZipFile(modelZip, 'r') as z:
        z.extractall(CDIR)
    remove(modelZip)
    print('Model installed!')

if exists(modelZip):
    try:
        with ZipFile(modelZip, 'r') as z:
            z.extractall(CDIR)
    except:
        installModel()

if not exists(modelDir):
    installModel()

net = dnn.readNet(pjoin(modelDir, 'yolov3.weights'), pjoin(modelDir, 'yolov3.cfg'))

def getOutputLayers(net):
    layerNames = net.getLayerNames()
    layers = net.getUnconnectedOutLayers()
    try:
        outputLayers = [layerNames[i[0] - 1] for i in layers]
    except:
        outputLayers = [layerNames[i - 1] for i in layers]
    return outputLayers

def predict(net, file):
    fileNames = pjoin(modelDir, 'yolov3.txt')

    image = imread(file)
    scale = 0.00392

    confThreshold = 0.5

    with open(fileNames, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    blob = dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(getOutputLayers(net))
    classesNames = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = int(argmax(scores))
            confidence = scores[classId]
            if confidence > confThreshold:
                classesNames.append(classes[classId])
    return classesNames

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def give():
	global used
	if request.method == 'POST':
	    if 'file' in request.files:
	        file = request.files['file']
	        fname = file.filename.lower()
	        if not 'jpg' in fname and not 'png' in fname:
	            return jsonify(error='WTF?! Where\'s image?(')
	        path = pjoin(CDIR, 'captcha.png')
	        file.save(path)
	        prediction = predict(net, path)
	        remove(path)
	        return jsonify(predict=prediction)
	    else:
	        return jsonify(error='Where\'s file?(')
	else:
		return jsonify(error='POST Method Only!!!')