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
import run_classifiers
import csv
from PIL import Image


TRINITY_DATA_PATH = r'TrainingData/data.csv'
TRINITY_DATA_PATH_SAVE = r'TrainingData/new_data.csv'
IMAGE_DATA_PATH = r'ImageData/'
SENSOR_TRIES = 10

def addData(label, data, dataFile):
    data = [label] + data
    temp = ""
    with open(dataFile, 'a+') as d:
        temp = " ".join(data)
        temp += '\n'
        d.write(temp)

def plotAudio (fs, signal):
    time = np.linspace(0,len(signal)/fs, num=len(signal))
    fig = plt.figure(1)
    plt.title("Trash Drop Audio Signal")
    plt.plot(time, signal)
    plt.show()

def classify(signal, hx, cap, camera, model):
    try:

        # take picture from camera
        print("taking picture...")
        timeStamp = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
        timeStamp = 'temp'
        imgName = IMAGE_DATA_PATH + timeStamp + '.jpg'
        camera.start_preview()
        camera.capture(imgName)
        time.sleep(3)
        camera.stop_preview()

        # get values from load sensor and capacitive sensor
        print("sensing load and capacitance")
        load_value = 0
        capacitive = 0
        for i in xrange(0, SENSOR_TRIES):
            # load sensing
            load_value += hx.get_weight(5)
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
            time.sleep(0.05)

        load_value /= SENSOR_TRIES

        print("getting audio features...")
        audioFeatures = extractFeatures.extractFeatures(44100, np.array(signal))

        # format data to pass to classifiers
        args = [str(load_value), str(capacitive)] + audioFeatures
        for i in xrange(0, len(args)):
            args[i] = str(args[i])

        # run classifiers on data
        print("running classifiers")
        knn_output, log_output, svm_output, rf_output = run_classifiers.run_classifiers(TRINITY_DATA_PATH, args)
        svm_indicies, svm_preds = svm_output
        knn_indicies, knn_preds = knn_output
        rf_indicies, rf_preds = rf_output
        log_indicies, log_preds = log_output

        '''
        svm_indicies, svm_preds = run_svm.run_svm(TRINITY_DATA_PATH, args)
        knn_indicies, knn_preds = run_knn.run_knn(TRINITY_DATA_PATH, args)
        rf_indicies, rf_preds = run_randomforest.run_randomforest(TRINITY_DATA_PATH, args)
        log_indicies, log_preds = run_log.run_log(TRINITY_DATA_PATH, args)
        #img_indicies, img_preds = run_NN.predict(model, imgName)
        '''

        max_prob_svm = max(svm_preds)
        max_arg_svm = svm_indicies[np.argmax(svm_preds)]

        max_prob_knn = max(knn_preds)
        max_arg_knn = knn_indicies[np.argmax(knn_preds)]

        max_prob_rf = max(rf_preds)
        max_arg_rf = rf_indicies[np.argmax(rf_preds)]

        max_prob_log = max(log_preds)
        max_arg_log = log_indicies[np.argmax(log_preds)]
        '''
        max_prob_NN = max(img_preds)
        max_arg_NN = img_indicies[np.argmax(img_preds)]

        if (max_prob_knn >= max_prob_NN):
            final_pred = max_arg_knn
        else:
            final_pred = max_arg_NN
        '''
        final_pred = 'potato'
        print("SVM prediction is..."+max_arg_svm)
        print("KNN prediction is..."+max_arg_knn)
        print("Random Forest prediction is..."+max_arg_rf)
        print("Logistic Regression prediction is..."+max_arg_log)
        print("Final prediction is..."+final_pred)

        addData(recieved, args, TRINITY_DATA_PATH_SAVE)

    except (KeyboardInterrupt, SystemExit):
        sys.exit()

def main():

    print("initializing sensors...")

    # initialize load sensor
    hx = HX711(5,6)
    hx.set_reading_format("LSB", "MSB")
    hx.set_reference_unit(-428.72)
    hx.reset()
    hx.tare()
    base_load = 0
    for i in xrange(0,10):
        base_load += hx.get_weight(5)
        hx.power_down()
        hx.power_up()
    base_load /= 10

    # initialize capacitive sensor
    cap = MPR121.MPR121()
    if not cap.begin():
        print('Error initializing MPR121.  Check your wiring!')
        sys.exit(1)
    last_touched = cap.touched()

    # initialize microphone
    card = 'sysdefault:CARD=Device'
    fs = 44100
    num_ms = 132300
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, card)
    inp.setchannels(1)
    inp.setrate(fs)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(32)

    totalLen = 0
    signal = []
    while (totalLen < fs * 5):
        l, data = inp.read()
        if (l > 0):
            signal += list(np.fromstring(data, 'int16'))
            totalLen += l

    # initialize camera
    camera = PiCamera()

    # initialize neural net model
    #model = run_NN.initializeNN()
    model = None
    print("you can start throwing your trash now");

    while (True):
        try:
            load_value = hx.get_weight(5)
            hx.power_down()
            hx.power_up()
            print("load value = "+str(load_value))

            totalLen = 0
            while (totalLen < fs * 1):
                l, data = inp.read()
                if (l > 0):
                    signal += list(np.fromstring(data, 'int16'))
                    totalLen += l
                    signal = signal[l:]


            if (load_value - base_load > 0.5):
                print("starting classification")
                classify(signal[len(signal)-44100*3:], hx, cap, camera, model)

            while(load_value - base_load > 0.5):
                load_value = hx.get_weight(5)
                hx.power_down()
                hx.power_up()

        except (KeyboardInterrupt, SystemExit):
            camera.close()
            GPIO.cleanup()
            sys.exit()


if __name__=="__main__":
    main()
