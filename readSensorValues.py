from hx711py.hx711 import HX711
import sys
import time
import RPi.GPIO as GPIO
import numpy as np
import matplotlib.pyplot as plt
import wave
import Adafruit_Python_MPR121.Adafruit_MPR121.MPR121 as MPR121
import subprocess
import extractFeatures
import run_svm

SVM_DATA_PATH = r'TrainingData/dummy.csv'
AUDIO_DATA_PATH = r'WaveFiles/test.wav'
LOAD_SENSOR_TRIES = 10

def plotAudio (waveFile):
    spf = wave.open(waveFile, 'r')
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'int16')
    fs = spf.getframerate()
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

    # get audio file
    subprocess.call('arecord --device=hw:1,0 --format S16_LE --rate 44100 -c1 -d 3 ' + AUDIO_DATA_PATH, shell=True)
    audioFeatures = extractFeatures.extractFeatures(AUDIO_DATA_PATH)

    # get values from load sensor and capacitive sensor
    count = LOAD_SENSOR_TRIES
    loadValue = 0
    print("\nsensing weight and capacitance...")

    while (count > 0):
        count -= 1

        try:
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

        except(KeyboardInterrupt, SystemExit):
            cleanAndExit()

    # print results to STDOUT
    loadValue /= LOAD_SENSOR_TRIES
    print("done sensing weight and capacitance\n")
    print("Data Features:")
    print("\tweight = " + str(loadValue))
    print("\tcapacitance = " + str(capacitive))
    print("\tamplitude = " + str(audioFeatures[0]))
    print("\tnumber of peaks = " + str(audioFeatures[1]))
    print("\tcentroid = " + str(audioFeatures[2]))
    print("\tspectrum = " + str(audioFeatures[3]))
    plotAudio(AUDIO_DATA_PATH)
    print("\npredicting recycling category...\n")

    # run SVM on data
    args = [str(loadValue), str(capacitive)] + audioFeatures
    run_svm.run_svm(SVM_DATA_PATH, args)

    # close sensors and exit
    cleanAndExit()

if __name__=="__main__":
    main()
