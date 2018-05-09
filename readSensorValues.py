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
import run_log
import run_randomforest
import run_NN
import csv
from PIL import Image


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
            # camera.start_preview()
            # camera.capture(imgName)
            # camera.stop_preview()

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
            print("\tMel-Freq Cep Coeff = " + str(audioFeatures[4]))
            plotAudio(fs, signal)
            print("predicting recycling category...")

            # format data to pass to classifiers
            args = [str(loadValue), str(capacitive)] + audioFeatures
            for i in xrange(0, len(args)):
                args[i] = str(args[i])

            # run classifiers on data
            # 0 = compost
            # 1 = metal
            # 2 = plastic
            # if highest probability is less than 50% then predict trash

            svm_indicies, svm_preds = run_svm.run_svm(TRINITY_DATA_PATH, args)
            knn_indicies, knn_preds = run_knn.run_knn(TRINITY_DATA_PATH, args)
            rf_indicies, rf_preds = run_randomforest.run_randomforest(TRINITY_DATA_PATH, args)
            log_indicies, log_preds = run_log.run_log(TRINITY_DATA_PATH, args)
            # img_indicies, img_preds = run_NN.predict(model, imgName)

            # max_prob_NN = max(img_preds)
            # max_arg_NN = img_indicies[np.argmax(img_preds)]
            max_prob_NN = 0.0
            max_arg_NN = 'trash'

            max_prob_svm = max(svm_preds)
            max_arg_svm = svm_indicies[np.argmax(svm_preds)]

            max_prob_knn = max(knn_preds)
            max_arg_knn = knn_indicies[np.argmax(knn_preds)]

            max_prob_rf = max(rf_preds)
            max_arg_rf = rf_indicies[np.argmax(rf_preds)]

            max_prob_log = max(log_preds)
            max_arg_log = log_indicies[np.argmax(log_preds)]

            if (max_prob_svm <= 0.45):
                max_arg_svm = 'trash'
            if (max_prob_knn <= 0.45):
                max_arg_knn = 'trash'
            if (max_prob_rf <= 0.45):
                max_arg_rf = 'trash'
            if (max_prob_log <= 0.45):
                max_arg_log = 'trash'
            # if (max_prob_NN <= 0.45):
            #     max_arg_NN = 'trash'

            print("SVM prediction is..."+max_arg_svm)
            print("KNN prediction is..."+max_arg_knn)
            print("Random Forest prediction is..."+max_arg_rf)
            print("Logistic Regression prediction is..."+max_arg_log)
            # print("NN prediction is..."+max_arg_NN)

            '''
            if (max_arg_knn == 'trash'):
                final_pred = max_arg_NN
            if (max_arg_NN == 'trash'):
                final_pred = max_arg_knn
            if (max_arg_knn != 'trash' and max_arg_NN != 'trash'):
                if (max_prob_knn > max_prob_NN):
                    final_pred = max_arg_knn
                else:
                    final_pred = max_arg_NN

            print("FINAL PREDICTION IS... " + final_pred)

            # save data
            val = raw_input("should I save this data point? ")
            if (val == 'yes'):
                val = raw_input("what is the category of this point? ")
                addData(val,args, TRINITY_DATA_PATH)
            '''

        except (KeyboardInterrupt, SystemExit):
            camera.close()
            GPIO.cleanup()
            sys.exit()

        except:
            continue

        '''
        except:
            print "\nrip something went wrong!"
            camera.close()
            GPIO.cleanup()
            sys.exit()
        '''


if __name__=="__main__":
    main()
