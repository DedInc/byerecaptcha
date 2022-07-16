from os import mkdir, remove
from os.path import join as pjoin, exists, dirname, abspath
from time import sleep, time
from random import uniform, randint
from itertools import product
from zipfile import ZipFile
from ntpath import split, basename
from cv2 import imread, dnn
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from requests import Session, post
from PIL import Image
from numpy import sqrt, argmax
from shutil import rmtree

cdir = dirname(abspath(__file__))
modelZip = pjoin(cdir, 'model.zip')
modelDir = pjoin(cdir, 'model')
picturesDir = pjoin(cdir, 'pictures')

def installModel():
    print('Model is not exists!\nDownloading... (230 MB)')
    from requests import get
    with open(modelZip, 'wb') as f:
        f.write(get('https://www.dropbox.com/s/bsb4qew5h0mvm1l/model.zip?dl=1').content)
    with ZipFile(modelZip, 'r') as z:
        z.extractall(cdir)
    remove(modelZip)
    print('Model installed!')

if exists(picturesDir):
    rmtree(picturesDir)

def getPage(url, binary=False, timeout=300):
    with Session() as session:
        response = session.get(url, timeout=timeout)
        if binary:
            return response.content
        return response.text

def getFileName(path):
    head, tail = split(path)
    return tail or basename(head)

def saveFile(file, data, binary=False):
    mode = "w" if not binary else "wb"
    with open(file, mode=mode) as f:
        f.write(data)

def isFrameAttachted(frameReference):
    try:
        driver.switch_to_frame(frameReference)
        driver.switch_to.parent_frame()
    except:
        return False
    else:
        return True

def hover(element):
    if element == CheckBox:
        driver.switch_to.frame(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe'))).get_attribute('name'))
    ActionChains(driver).move_to_element(element).perform()

def clickReloadButton():
    driver.switch_to.frame(imageFrame)
    driver.find_element_by_id('recaptcha-reload-button').click()
    driver.switch_to.parent_frame()

def clickVerify():
    driver.switch_to.frame(imageFrame)
    driver.find_element_by_id('recaptcha-verify-button').click()
    driver.switch_to.parent_frame()

def getFrames(invisible=False):
    global recaptchaFrame, CheckBox, imageFrame
    recaptchaFrame = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
    driver.switch_to.frame(recaptchaFrame)
    if not invisible:
        CheckBox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "recaptcha-anchor")))
    driver.switch_to.parent_frame()
    while True:
        frames = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'iframe[src*="api2/bframe"]')))
        for frame in frames:
            if not isFrameAttachted(frame):
                continue
        break
    for frame in frames:
        driver.switch_to.frame(frame)
        if 'recaptcha-image-button' in driver.page_source:
            imageFrame = frame
        driver.switch_to.parent_frame()

def clickCheckBox():
    hover(CheckBox)
    sleep(uniform(0.5, 0.7))
    CheckBox.click()
    driver.switch_to.parent_frame()

def getRecaptchaResponse():
    if driver.execute_script('return document.getElementsByName("g-recaptcha-response")[0].value !== ""'):
        return driver.execute_script('return document.getElementsByName("g-recaptcha-response")[0].value')
    return False

def getImageUrl():
    driver.switch_to.frame(imageFrame)
    imageUrl = driver.execute_script('return document.getElementsByClassName("rc-image-tile-wrapper")[0].getElementsByTagName("img")[0].src')
    driver.switch_to.parent_frame()
    return imageUrl

def downloadImage():
    global download
    download = getImageUrl()
    return getPage(download, binary=True)

def getImages():
    global pieces
    driver.switch_to.frame(imageFrame)
    pieces = driver.execute_script('return document.getElementsByTagName("td").length')
    driver.switch_to.parent_frame()

def createFolder(title, image):
    global curImagePath, imageHash
    imageHash = hash(image)
    if not exists(picturesDir):
        mkdir(picturesDir)
    if not exists(pjoin(picturesDir, f'{title}')):
        mkdir(pjoin(picturesDir, f'{title}'))
    if not exists(pjoin(picturesDir, 'tmp')):
        mkdir(pjoin(picturesDir, 'tmp'))
    curImagePath = pjoin(pjoin(picturesDir, f'{title}'))
    if not exists(curImagePath):
        mkdir(curImagePath)

def searchTitle(title):
    classes = ('bus', 'car', 'bicycle', 'fire_hydrant', 'crosswalk', 'stair', 'bridge', 'traffic_light',
               'vehicles', 'motorbike', 'boat', 'chimneys')
    possibleTitles = (
        ('autobuses', 'autobús', 'bus', 'buses', 'автобус', 'автобусы'),
        ('automóviles', 'cars', 'car', 'coches', 'coche', 'автомобили'),
        ('bicicletas', 'bicycles', 'bicycle', 'bici', 'велосипеды'),
        ('boca de incendios', 'boca_de_incendios', 'una_boca_de_incendios', 'fire_hydrant', 'fire_hydrants',
         'a_fire_hydrant', 'bocas_de_incendios', 'пожарные гидранты', 'пожарные_гидранты'),
        ('cruces_peatonales', 'crosswalk', 'crosswalks', 'cross_walks', 'cross_walk', 'pasos_de_peatones', 'пешеходные переходы', 'пешеходные_переходы'),
        ('escaleras', 'stair', 'stairs', 'лестницы'),
        ('puentes', 'bridge', 'bridges', 'мосты'),
        ('semaforos', 'semaphore', 'semaphores', 'traffic_lights', 'traffic_light', 'semáforos', 'светофоры', 'светофор'),
        ('vehículos', 'vehicles', 'транспортные средства', 'транспортные_средства'),
        ('motocicletas', 'motocicleta', 'motorcycle', 'motorcycle', 'motorbike', 'мотоциклы', 'мотоцикл'),
        ('boat', 'boats', 'barcos', 'barco', 'лодки', 'лодка'),
        ('chimeneas', 'chimneys', 'chimney', 'chimenea', 'дымовые трубы', 'дымовые_трубы')
    )
    i = 0
    for objects in possibleTitles:
        if title in objects:
            return classes[i]
        i += 1
    return title

def getStartData():
    global title
    title = searchTitle(descriptionElement.replace(' ', '_'))
    image = downloadImage()
    createFolder(title, image)
    filePath = pjoin(curImagePath, f'{imageHash}_{title}.jpg')
    saveFile(filePath, image, binary=True)
    getImages()
    return filePath

def checkDetection(timeout):
    global content, descriptionElement
    timeout = time() + timeout
    while time() < timeout:
        result = driver.execute_script('return document.getElementsByName("g-recaptcha-response")[0].value !== ""')
        if result:
            return result
        while True:
            try:
                driver.switch_to.frame(imageFrame)
                content = driver.page_source
                descriptionElement = driver.execute_script('return document.getElementsByTagName("strong")[0].textContent')
                break
            except:
                getFrames()
        driver.switch_to.parent_frame()
        if 'Try again later' in content:
            return 'detected'
        elif 'Press PLAY to listen' in content:
            return 'solve'
        else:
            result = driver.execute_script('return document.getElementsByName("g-recaptcha-response")[0].value !== ""')
            if result:
                return result

def getOutputLayers(net):
    layerNames = net.getLayerNames()
    layers = net.getUnconnectedOutLayers()
    try:
        outputLayers = [layerNames[i[0] - 1] for i in layers]
    except:
        outputLayers = [layerNames[i - 1] for i in layers]
    return outputLayers

def predict(file, net):
    if serverSolve:
        with open(file, 'rb') as f:
            return post(serverUrl, files={'file': (getFileName(file), f)}).json()['predict']
    else:
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

def splitImage(imageObj, pieces, save_to, name):
    width, height = imageObj.size
    rowLength = int(sqrt(pieces))
    interval = width // rowLength
    for x, y in product(range(rowLength), repeat=2):
        cropped = imageObj.crop((interval * x, interval * y, interval * (x + 1), interval * (y + 1)))
        cropped.save(pjoin(save_to, f'{name}_{y * rowLength + x}.jpg'))

def choose(imagePath):
    selected = []
    if pieces == 9:
        imageObj = Image.open(imagePath)
        splitImage(imageObj, pieces, curImagePath, imageHash)
        for i in range(pieces):
            result = predict(pjoin(curImagePath, f'{imageHash}_{i}.jpg'), net)
            if title.replace('_', ' ') in result:
                selected.append(i)
        remove(imagePath)
    return selected

def clickImage(list_id):
    driver.switch_to.frame(imageFrame)
    elements = driver.find_elements_by_css_selector('.rc-imageselect-tile')
    for i in list_id:
        elements[i].click()
    driver.switch_to.parent_frame()

def isOneSelected():
    driver.switch_to.frame(imageFrame)
    ev = driver.execute_script('return document.getElementsByClassName("rc-imageselect-tileselected").length === 0')
    driver.switch_to.parent_frame()
    return ev

def getImagesBlock(images):
    imagesUrl = []
    driver.switch_to.frame(imageFrame)
    for element in images:
        imageUrl = driver.execute_script(f'return document.getElementsByClassName("rc-image-tile-wrapper")[{element}].getElementsByTagName("img")[0].src')
        imagesUrl.append(imageUrl)
    driver.switch_to.parent_frame()
    return imagesUrl

def cycleSelected(selected):
    while True:
        checkDetection(randint(5, 8))
        images = getImagesBlock(selected)
        newSelected = []
        i = 0
        for imageUrl in images:
            if images != download:
                image = getPage(imageUrl, binary=True)
                createFolder(title, image)
                filePath = pjoin(
                    curImagePath, f'{imageHash}_{title}.jpg')
                saveFile(filePath, image, binary=True)

                result = predict(filePath, net)
                if title == 'vehicles':
                    if 'car' in result or 'truck' in result or 'bus' in result:
                        newSelected.append(selected[i])
                if title == 'motorcycles':
                    if 'car' in result or 'bicycle' in result or 'motorcycles' in result:
                        newSelected.append(selected[i])
                if (title != 'vehicles'
                        and title.replace('_', ' ') in result):
                    newSelected.append(selected[i])
            i += 1
        if newSelected:
            clickImage(newSelected)
        else:
            break

def isFinish():
    result = checkDetection(5)
    if result:
        return True
    return False

def isNext():
    imageUrl = getImageUrl()
    return False if imageUrl == download else True

def solveByImage():
    global net
    if not serverSolve:
        net = dnn.readNet(pjoin(modelDir, 'yolov3.weights'), pjoin(modelDir, 'yolov3.cfg'))
    else:
        net = None
    while True:
        result = checkDetection(3)
        if result:
            break
        filePath = getStartData()
        if pieces == 16:
            clickReloadButton()
        elif pieces == 9:
            choices = choose(filePath)
            clickImage(choices)
            if choices:
                if isOneSelected():
                    cycleSelected(choices)
                    clickVerify()
                    if not isNext() and not isFinish():
                        clickReloadButton()
                else:
                    clickVerify()
                    if not isNext() and not isFinish():
                        clickReloadButton()
            else:
                clickReloadButton()

def solveImage():
    solveByImage()
    result = getRecaptchaResponse()
    if result:
        return result

def solveRecaptcha(browser, server='', invisible=False):
    global driver, serverSolve, serverUrl

    if server == '':
        if exists(modelZip):
            try:
                with ZipFile(modelZip, 'r') as z:
                    z.extractall(cdir)
            except:
                installModel()

        if not exists(modelDir):
            installModel()
        serverSolve = False
    else:
        serverUrl = server
        serverSolve = True

    driver = browser    
    if not invisible:
        getFrames(invisible)
        clickCheckBox()
    while True:
        try:
            getFrames(invisible)
            driver.switch_to.frame(imageFrame)
            driver.switch_to.parent_frame()
            break
        except:
            pass
    result = solveImage()
    rmtree(picturesDir)
    if result:
        return result