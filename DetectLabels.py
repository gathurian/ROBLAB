from naoqi import *
import DetectlabelsGoogle

app = qi.Application(["--qi-url=192.168.1.102:9559"])
app.start()
session = app.session
tts = session.service("ALTextToSpeech")
tts.resetSpeed()

path = 'C:\Users\Alex\Pictures\Pepper\\2018-5-14-15-48.jpg'
foundLabel = False

label = DetectlabelsGoogle.detect_labels(path)

tts.say("I can see the following things in that picture:")
tts.setParameter("speed", 80)
tts.say(str(label))
tts.resetSpeed()

labelsFileWrite = open("labels.txt", "a")
labelsFileWrite.write("%s \n" % str(label))
labelsFileWrite.close()



