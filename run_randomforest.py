from sklearn.ensemble import RandomForestClassifier
import os, math, sys, numpy, csv

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
					temp.append(float(row[i]))
				X.append(temp)
			else:
				Y.append(labels[row[0]])
				temp = []
				for i in xrange(1, len(row)):
					temp.append(float(row[i]))
				X.append(temp)

		return X, Y, labels, indeces

def train(X, Y, predict1, predict2, predict3, predict4, predict5, predict6, indeces):
	clf = RandomForestClassifier(n_jobs=2, random_state=0)
	clf.fit(X, Y)
	test = [[predict1, predict2, predict3, predict4, predict5, predict6]]
	prediction = clf.predict(test)
	print("Random Forst prediction is : " + indeces[prediction[0]])

def plot_contours(ax, clf, xx, yy, **params):

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    out = ax.contourf(xx, yy, Z, **params)
    return out

def run_randomforest(inputData, new_data):
    predict1 = new_data[0]
    predict2 = new_data[1]
    predict3 = new_data[2]
    predict4 = new_data[3]
    predict5 = new_data[4]
    predict6 = new_data[5]
    X, Y, labels, indeces = parseData(inputData)
    train(X, Y, float(predict1), float(predict2), float(predict3), float(predict4), float(predict5), float(predict6), indeces)


# if __name__ == '__main__':
# 	inputData = sys.argv[1]
# 	predict1 = sys.argv[2]
# 	predict2 = sys.argv[3]
# 	predict3 = sys.argv[4]
# 	predict4 = sys.argv[5]
# 	predict5 = sys.argv[6]
# 	predict6 = sys.argv[7]

# 	X, Y, labels, indeces = parseData(inputData)
# 	train(X, Y, float(predict1), float(predict2), float(predict3), float(predict4), float(predict5), float(predict6), indeces)
