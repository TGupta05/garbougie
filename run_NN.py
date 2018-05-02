import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import keras
from keras.preprocessing import image
from keras.models import load_model
from keras.applications.inception_v3 import preprocess_input


target_size = (229, 229) #fixed size for InceptionV3 architecture
labels = ("apple", "banana", "beverage_can", "bottle_cap", "food_can", "jar_lid", "lemon", "milk_carton", "orange", "takeout_container", "utensil", "water_bottle")


def predict(model, img):
    labels = ("apple", "banana", "beverage_can", "bottle_cap", "food_can", "jar_lid", "lemon", "milk_carton", "orange", "takeout_container", "utensil", "water_bottle")
    if img.size != target_size:
        img = img.resize(target_size)

    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)

    compressed_preds = [0]*3
    compressed_preds[0] = preds[0]+preds[1]+preds[6]+preds[8]
    compressed_preds[1] = preds[2]+preds[3]+preds[4]+preds[5]
    compressed_preds[2] = preds[7]+preds[9]+preds[10]+preds[11]

    print("ImageNet prediction is : " + labels[np.argmax(pred)])
    return {0:"compost", 1:"metal", 2:"plastic"}, compressed_preds


def plot_preds(image, preds):
    """Displays image and the top-n predicted probabilities in a bar graph
    Args:
    image: PIL image
    preds: list of predicted labels and their probabilities
    """
    plt.imshow(image)
    plt.axis('off')

    plt.figure()
    labels = ("apple", "banana", "beverage_can", "bottle_cap", "food_can", "jar_lid", "lemon", "milk_carton", "orange", "takeout_container", "utensil", "water_bottle")
    plt.barh([0, 1], preds, alpha=0.5)
    plt.yticks([0, 1], labels)
    plt.xlabel('Probability')
    plt.xlim(0,1.01)
    plt.tight_layout()
    plt.show()


def initializeNN():
    return load_model('inceptionv3-ft.model')



