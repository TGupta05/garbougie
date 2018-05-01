from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import audioFeatureExtraction
import matplotlib.pyplot as plt

import numpy as np
import scipy.signal
import wave
import sys
import pylab
# from PIL import Image
import matplotlib.pyplot as plt
eps = 0.00000001



def getMaxPeak(signal, frate):
	#peak frquency
	data = np.array(signal)

	w = np.fft.fft(data)
	freqs = np.fft.fftfreq(len(w))

	idx = np.argmax(np.abs(w))
	freq = freqs[idx]
	freq_in_hertz = abs(freq * frate)

	return freq

def getAmplitudePeak(signal):
	indexes = scipy.signal.argrelextrema(
		np.array(signal),
		 comparator=np.greater,order=2
	)
	return max(signal)

def getNumPeak(signal):
	#using spectral entropy to find peaks
	super_threshold_indices = signal < 0.2
	signal[super_threshold_indices] = 0
	indexes = scipy.signal.argrelextrema(
		np.array(signal),
		 comparator=np.greater,order=2
	)
	return len(indexes[0])

def energy(signal):
	"""Computes signal energy of frame"""
	signal = np.asarray(signal)
	return np.sum(signal ** 2) / np.float64(len(signal))

def stSpectralCentroidAndSpread(X, fs):
	X = abs(np.fft.fft(X))
	X = X / len(X)
	ind = (np.arange(1, len(X) + 1)) * (fs/(2.0 * len(X)))

	Xt = X.copy()
	Xt = Xt / Xt.max()
	NUM = np.sum(ind * Xt)
	DEN = np.sum(Xt) + eps

	# Centroid:
	C = (NUM / DEN)

	# Spread:
	S = np.sqrt(np.sum(((ind - C) ** 2) * Xt) / DEN)

	# Normalize:
	C = C / (fs / 2.0)
	S = S / (fs / 2.0)

	return (C*fs, S*fs)


def stHarmonic(frame, fs):
	"""
	Computes harmonic ratio and pitch
	"""
	M = np.round(0.016 * fs) - 1
	R = np.correlate(frame, frame, mode='full')

	g = R[len(frame)-1]
	R = R[len(frame):-1]

	# estimate m0 (as the first zero crossing of R)
	[a, ] = np.nonzero(np.diff(np.sign(R)))

	if len(a) == 0:
		m0 = len(R)-1
	else:
		m0 = a[0]
	if M > len(R):
		M = len(R) - 1

	Gamma = np.zeros((M), dtype=np.float64)
	CSum = np.cumsum(frame ** 2)
	Gamma[m0:M] = R[m0:M] / (np.sqrt((g * CSum[M:m0:-1])) + eps)

	ZCR = stZCR(Gamma)

	if ZCR > 0.15:
		HR = 0.0
		f0 = 0.0
	else:
		if len(Gamma) == 0:
			HR = 1.0
			blag = 0.0
			Gamma = np.zeros((M), dtype=np.float64)
		else:
			HR = np.max(Gamma)
			blag = np.argmax(Gamma)

		# Get fundamental frequency:
		f0 = fs / (blag + eps)
		if f0 > 5000:
			f0 = 0.0
		if HR < 0.1:
			f0 = 0.0

	return (HR, f0)

def highpass_filter(y, sr):
  filter_stop_freq = 70  # Hz
  filter_pass_freq = 100  # Hz
  filter_order = 1001

  # High-pass filter
  nyquist_rate = sr / 2.
  desired = (0, 0, 1, 1)
  bands = (0, filter_stop_freq, filter_pass_freq, nyquist_rate)
  filter_coefs = signal.firls(filter_order, bands, desired, nyq=nyquist_rate)

  # Apply high-pass filter
  filtered_audio = signal.filtfilt(filter_coefs, [1], y)
  return filtered_audio


def extractFeatures(fs, signal):
	'''
        spf = wave.open('WaveFiles/test.wav', 'r')
	signal = spf.readframes(-1)
	fs = spf.getframerate()
	signal = np.fromstring(signal, 'int16')
	time = np.linspace(0,len(signal)/fs, num=len(signal))
        '''
	F,Y = audioFeatureExtraction.mtFeatureExtraction(signal, fs, 0.025*fs, 0.025*fs,  0.050*fs, 0.025*fs);

	amplitudePeak = getAmplitudePeak(signal)
	numPeaks = getNumPeak(F[5,:])
	maxPeak = getMaxPeak(signal, fs)
	centroid, spectrum = stSpectralCentroidAndSpread(signal, fs)
        return [amplitudePeak, numPeaks, centroid, spectrum]

