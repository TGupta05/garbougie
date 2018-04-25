from sklearn import svm
import os, math, sys, numpy, csv

NUMBER_NEIGHBORS=2

def parseData(inputFile):
	with open(inputFile, 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter= ' ', quotechar='|')

		labels = dict()
		X = []
		Y  = []
		index = 1
		data = []
		indeces = dict()
		index = 0
		for row in spamreader:
			if len(row) == 0:
				continue
			if row[0] not in labels:
				labels[row[0]] = index
				indeces[index] = row[0]
				Y.append(labels[row[0]])
				index += 1
				temp = []
				for i in xrange(1, len(row)):
					temp.append(row[i])
				X.append(temp)
			else:
				Y.append(labels[row[0]])
				temp = []
				for i in xrange(1, len(row)):
					temp.append(row[i])
				X.append(temp)

		return X, Y, labels, indeces

def predict(X, Y, predict1, predict2, predict3, predict4, predict5, predict6, indeces):
	knn = dict()
	for i in xrange(0, len(X)):
		temp = X[i]	
		distance = math.sqrt(math.pow((float(temp[0])-predict1)/60.0,2) + math.pow((float(temp[1])-predict2)/2,2) + math.pow((float(temp[2])-predict3)/31000,2) + math.pow((float(temp[3])-predict4)/4,2) + math.pow((float(temp[4])-predict5),2) + math.pow((float(temp[5])-predict6),2))
		if len(knn) < NUMBER_NEIGHBORS:
			knn[distance] = i 
		else:
			maxDistance = -1
			for dis in knn:
				if dis > maxDistance:
					maxDistance = dis
			if distance < maxDistance:
				knn.pop(maxDistance)
				knn[distance] = i
			print "here"

	zeroCount = 0
	oneCount = 0
	twoCount = 0
	for key in knn:
		index = knn[key]
		if Y[index] == 0:
			zeroCount += 1
		if Y[index] == 1:
			oneCount += 1
		if Y[index] == 2:
			twoCount += 1
	if zeroCount > oneCount and zeroCount > twoCount:
		prediction = indeces[0]
	elif oneCount > zeroCount and oneCount > twoCount:
		prediction = indeces[1]
	else:
		prediction = indeces[2]

	print("KNN prediction is : " + prediction)

def run_knn(inputData, new_data):
	predict1 = new_data[0]
	predict2 = new_data[1]
	predict3 = new_data[2]
	predict4 = new_data[3]
	predict5 = new_data[4]
	predict6 = new_data[5]

	X, Y, labels, indeces = parseData(inputData)
	predict(X, Y, float(predict1), float(predict2), float(predict3), float(predict4), float(predict5), float(predict6), indeces)

if __name__ == '__main__':
	inputData = sys.argv[1]
	predict1 = sys.argv[2]
	predict2 = sys.argv[3]
	predict3 = sys.argv[4]
	predict4 = sys.argv[5]
	predict5 = sys.argv[6]
	predict6 = sys.argv[7]

	X, Y, labels, indeces = parseData(inputData)
	predict(X, Y, float(predict1), float(predict2), float(predict3), float(predict4), float(predict5), float(predict6), indeces)

