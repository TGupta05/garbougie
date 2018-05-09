import sys



if __name__ == "__main__":
    tp = float(sys.argv[1])
    tn = float(sys.argv[2])
    fp = float(sys.argv[3])
    fn = float(sys.argv[4])
    
    precision = tp/(tp + fp)
    recall = tp*(tp + fn)

    f1 = 2/((1/recall) + (1/precision))
    print f1
