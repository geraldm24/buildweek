import numpy as np
import keras.models
from keras.models import model_from_json
from scipy.misc import imread, imresize,imshow
import tensorflow as tf
import os 

JsonPath = os.path.join(os.path.dirname(__file__),"data",
"model_architecture.json")
 
Modelweights = os.path.join(os.path.dirname(__file__),"data","model_weights.h5")


def init(): 
	json_file = open(JsonPath,'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)
	#load weights into new model
	loaded_model.load_weights(Modelweights)
	print("Loaded Model from disk")
	#compile and evaluate loaded model
	loaded_model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
	return loaded_model