from hx711py.hx711 import HX711
from picamera import PiCamera
import sys
import alsaaudio
import time
from time import gmtime, strftime
import RPi.GPIO as GPIO
import numpy as np
import matplotlib.pyplot as plt
import wave
import Adafruit_Python_MPR121.Adafruit_MPR121.MPR121 as MPR121
import subprocess
import extractFeatures
import run_svm
import run_knn
import run_randomforest
import run_NN
import csv

TRINITY_DATA_PATH = r'TrainingData/data.csv'
AUDIO_DATA_PATH = r'WaveFiles/test.wav'
IMAGE_DATA_PATH = r'ImageData/'
LOAD_SENSOR_TRIES = 10

def addData(label, data, dataFile):
    data = [label] + data
    temp = ""
    with open(dataFile, 'a+') as d:
        temp = " ".join(data)
        temp += '\n'
        d.write(temp)


def plotAudio (fs, signal):
    '''
    waveFile = 'WaveFiles/test.wav'
    spf = wave.open(waveFile, 'r')
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'int16')
    fs = spf.getframerate()
    '''
    time = np.linspace(0,len(signal)/fs, num=len(signal))
    fig = plt.figure(1)
    plt.title("Trash Drop Audio Signal")
    plt.plot(time, signal)
    plt.show()

def cleanAndExit():
    GPIO.cleanup()
    print "\nBye!"
    sys.exit()

def main():

    print("initializing sensors...\n")

    # initialize load sensor
    hx = HX711(5,6)
    hx.set_reading_format("LSB", "MSB")
    hx.set_reference_unit(-428.72)
    hx.reset()
    hx.tare()

    # initialize capacitive sensor
    cap = MPR121.MPR121()
    if not cap.begin():
        print('Error initializing MPR121.  Check your wiring!')
        sys.exit(1)
    last_touched = cap.touched()
    capacitive = 0;

    # initialize microphone
    card = 'sysdefault:CARD=Device'
    fs = 44100
    num_ms = 132300
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, card)
    inp.setchannels(1)
    inp.setrate(fs)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(32)

    # initialize camera
    camera = PiCamera()
    timeStamp = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    timeStamp = 'temp'
    cameraPath = IMAGE_DATA_PATH + timeStamp + '.jpg'
    camera.capture(cameraPath)

    # initialize neural net model
    # model = run_NN.initializeNN()

    while (True):

        try:
            val = raw_input("\nPRESS ANY KEY TO START ")

            print("start recording...")
            totalLen = 0
            signal = []
            while (totalLen < fs * 3):
                l, data = inp.read()
                if (l > 0):
                    signal += list(np.fromstring(data, 'int16'))
                    totalLen += l
            audioFeatures = extractFeatures.extractFeatures(fs, np.array(signal))
            print("done recording...")

            print("capturing image...")
            timeStamp = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
            timeStamp = 'temp'
            imgName = IMAGE_DATA_PATH + timeStamp + '.jpg'
            camera.capture(imgName)

            # get values from load sensor and capacitive sensor
            count = LOAD_SENSOR_TRIES
            loadValue = 0
            print("sensing weight and capacitance...")

            while (count > 0):
                count -= 1

                # load sensing
                loadValue += hx.get_weight(5)
                hx.power_down()
                hx.power_up()

                # capacitive sensing
                current_touched = cap.touched()
                for i in range(12):
                    pin_bit = 1 << i
                    if ((current_touched & pin_bit) and (last_touched & pin_bit)):
                        capacitive = 1
                last_touched = current_touched

                # wait
                time.sleep(0.1)

            # print results to STDOUT
            loadValue /= LOAD_SENSOR_TRIES
            print("Data Features:")
            print("\tweight = " + str(loadValue))
            print("\tcapacitance = " + str(capacitive))
            print("\tamplitude = " + str(audioFeatures[0]))
            print("\tnumber of peaks = " + str(audioFeatures[1]))
            print("\tcentroid = " + str(audioFeatures[2]))
            print("\tspectrum = " + str(audioFeatures[3]))
            plotAudio(fs, signal)
            print("predicting recycling category...")

            # format data to pass to classifiers
            args = [str(loadValue), str(capacitive)] + audioFeatures
            for i in xrange(0, len(args)):
                args[i] = str(args[i])

            # run classifiers on data
            run_svm.run_svm(TRINITY_DATA_PATH, args)
            run_knn.run_knn(TRINITY_DATA_PATH, args)
            run_randomforest.run_randomforest(TRINITY_DATA_PATH, args)
            #run_NN.predict(model, imgName)

            # save data
            val = raw_input("should I save this data point? ")
            if (val == 'yes'):
                val = raw_input("what is the category of this point? ")
                addData(val,args, TRINITY_DATA_PATH)

        except (KeyboardInterrupt, SystemExit):
            camera.close()
            GPIO.cleanup()
            sys.exit()

        except:
            print "\nrip something went wrong!"
            camera.close()
            GPIO.cleanup()
            sys.exit()


if __name__=="__main__":
    main()
