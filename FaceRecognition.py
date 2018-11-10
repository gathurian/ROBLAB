import datetime

from naoqi import *
from time import sleep
from threading import Lock
import DetectlabelsGoogle

ROBOT_IP = '192.168.1.102'
ROBOT_PORT = 9559


# path in which taken images will be saved
PICTURE_PATH = '/home/nao/recordings/cameras/'


class MyFaceRec(ALModule):
    """A Module to recognize persons"""
    subscriber = None  # type: object

    def __init__(self, name):
        ALModule.__init__(self, name)
        self.mutex = Lock()
        #Create necessary Proxies
        try:
            self.faceProxy = ALProxy("ALPeoplePerception")
        except Exception, fpError:
            raise fpError
        try:
            self.memProxy = ALProxy("ALMemory")
        except Exception, memError:
            raise memError
        try:
            self.cameraProxy = ALProxy("ALPhotoCapture")
            # set resolution of image to 1280*960px
            self.cameraProxy.setResolution(3)
            self.cameraProxy.setPictureFormat("jpg")
        except Exception, camError:
            raise camError

        try:
            self.tts = ALProxy("ALTextToSpeech", ROBOT_IP, 9559)
            #reset the speaking-speed
            self.tts.resetSpeed()
        except Exception, ttsErr:
            raise ttsErr

    def onLoad(self):
        self.faceProxy.setGraphicalDisplayEnabled(True)
        self.faceProxy.setMovementDetectionEnabled(True)
        self.faceProxy.setTimeBeforePersonDisappears(5)
        self.faceProxy.setMaximumDetectionRange(0.5)

    def onInput_onStart(self):
        self.mutex.acquire()
        try:
            # on Event 'justArrived' (person walks into vision-field of Pepper), in Module 'pythonFaceRec' execute method 'onPeaopleDetected'
            self.memProxy.subscribeToEvent("justArrived", "pythonFaceRec", "onPeopleDetected")
            print "I'm starting to look for people"
            self.takePicture()
        except Exception, peopleErr:
            self.mutex.release()
            print "Error with creating subscription"
            print peopleErr
            self.onUnload()
            raise peopleErr
        self.mutex.release()

    def onUnload(self):
        self.mutex.acquire()
        try:
            # unsubscribe from the event subscribed in line 56
            self.memProxy.unsubscribeToEvent("justArrived", self.getName())
        except Exception, unsubErr:
            self.mutex.release()
            print "Error with unsubscribing to PeopleDetected"
            print unsubErr
            exit(1)
            raise unsubErr
        print "I'm done"
        self.mutex.release()

    def takePicture(self):
        # get current Date and time
        date = datetime.datetime.now()
        year = str(date.year)
        month = str(date.month)
        day = str(date.day)
        hour = str(date.hour)
        minute = str(date.minute)
        # create image-name from current Year, Month, Day, Hour and Minute
        img = year + "-" + month + "-" + day + "-" + hour + "-" + minute
        sleep(3)
        self.tts.say("Smile for the camera. I'm taking a picture")
        # take a picture with the name [Year-Month-Day-Hour-Minute] in the specified PICTURE_PATH (line 11)
        self.cameraProxy.takePicture(PICTURE_PATH, img + ".jpg")
        # execute Googles Vision Api detect_labels method on picture
        # TODO: Get shit working with picture taken moments ago
        # label = DetectlabelsGoogle.detect_labels("C:\Users\Alex\Pictures\Pepper\\2018-5-14-15-48.jpg")
        # self.tts.say("I can see the following things in that picture:")
        # self.tts.setParameter("speed", 80)
        # self.tts.say(str(label))
        # print "comparing to older labels..."
        # self.compareLabels("labels.txt", label)
        # # write the found labels into the specified file
        # self.writeLabelsToFile("labels.txt", label)

    def onPeopleDetected(value):
        print "I've seen somebody!"

    def writeLabelsToFile(self, textfile, label):
        # open the given textfile in append-mode (so it doesnt overwrite existing labels)
        labelsFileWrite = open(textfile, "a")
        # write the given label in the file
        labelsFileWrite.write("%s \n" % label)
        # close the file again
        labelsFileWrite.close()

    def readLabelsFromFile(self, textfile):
        # open the given textfile in read-mode
        labelsFileRead = open(textfile, "r")
        # create a list with all existing label-lines. One Element per Line
        existingLabels = labelsFileRead.read().splitlines()
        # close the file again
        labelsFileRead.close()
        # return that list.
        return existingLabels

    def compareLabels(self, textfile, labels):
        labelsList = self.readLabelsFromFile(textfile)
        # comparing the given labels (labels) with the already existing labes in the file (labelsList)
        list(set(labels) & set(labelsList))


global broker
broker = ALBroker("pythonBroker", "0.0.0.0", 0, ROBOT_IP, ROBOT_PORT)
global pythonPeopleModule
pythonPeopleModule = MyFaceRec('pythonFaceRec')
pythonPeopleModule.onLoad()
pythonPeopleModule.onInput_onStart()
sleep(10)
pythonPeopleModule.onUnload()
