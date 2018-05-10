from sklearn import svm
import os, math, sys, numpy, csv

NUMBER_NEIGHBORS=4

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
                #need to add new feature weightings
		distance = math.sqrt(math.pow((float(temp[0])-predict1)/5.0,2) + math.pow((float(temp[1])-predict2)/100,2) + math.pow((float(temp[2])-predict3)/5000,2) + math.pow((float(temp[3])-predict4)/20,2) + math.pow((float(temp[4])-predict5)/15,2) + math.pow((float(temp[5])-predict6)/600,2))

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

        total = 0.0 + zeroCount + oneCount + twoCount
        probs = [zeroCount/total, oneCount/total, twoCount/total]
        return indeces, probs

def run_knn(inputData, new_data):
	predict1 = new_data[0]
	predict2 = new_data[1]
	predict3 = new_data[2]
	predict4 = new_data[3]
	predict5 = new_data[4]
	predict6 = new_data[5]

	X, Y, labels, indeces = parseData(inputData)
	return predict(X, Y, float(predict1), float(predict2), float(predict3), float(predict4), float(predict5), float(predict6), indeces)

