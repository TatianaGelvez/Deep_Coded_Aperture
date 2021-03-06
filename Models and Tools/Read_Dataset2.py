import tensorflow as tf
import os
from matplotlib import pyplot as plt
from IPython import display
from IPython.display import clear_output
from PIL import Image

from os import listdir
from os.path import isfile, join

import numpy as np
import scipy.io
import pandas as pd
from scipy.io import loadmat


from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.models import *

#---------------------defined function used -------------------------------------------------------------------


# Defined protocol of input and ouput (it is recommended only read, not applied operator here, but it is possible)

def Input_image_jpg(image):
    im=np.array(Image.open(image))
    return im/np.max(im)


def Input_image_class(image,class_n):
    im = loadmat(image).get('depth_map')
    im= tf.keras.utils.to_categorical(im, num_classes=class_n)
    return im

def Oput_image_class(image,class_n):
    im = loadmat(image).get('label')
    im = tf.keras.utils.to_categorical(im, num_classes=class_n)
    return im

def Input_image(image):
    im=np.array(Image.open(image))
    im=np.expand_dims(im,axis=-1)
    return im/np.max(im)

def Oput_image_mat(image):
    im = loadmat(image).get('cube')
    return im

def Oput_image(image):
    im=np.array(Image.open(image))
    im = np.expand_dims(im,axis=-1)
    return im / np.max(im)


def load_sambles(data):
  data = data[['inimg']]
  inimg_name = list(data.iloc[:,0])
  samples = []
  for samp in inimg_name:
    samples.append(samp)
  return samples


class DataGenerator2(tf.keras.utils.Sequence):
    def __init__(self, samples,PATH,batch_size=1,dim_input=(512, 512, 3), shuffle=True, dim_oput=(512, 512, 3), dim_input2=(512, 512, 3),ty='mat'):
        'Initialization'
        self.dim_input = dim_input
        self.dim_input2 = dim_input2
        self.dim_oput = dim_oput
        self.batch_size = batch_size
        self.list_images = samples
        self.shuffle = shuffle
        self.PATH = PATH
        self.ty = ty
        self.on_epoch_end()


    # falta __data_generation
    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(len(self.list_images) / self.batch_size)

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indexes of the batch
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        # Find list of IDs
        images_name = [self.list_images[k] for k in indexes]

        # Generate data
        X, y = self.__data_generation(images_name)
        return X, y

    def on_epoch_end(self):
        'Update indexes after each epoch'
        self.indexes = np.arange(len(self.list_images))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, images_names):
        'Generates data containing batch_size samples'  # X : (n_samples, *dim, n_channels)
        # Initialization

        X = np.empty((self.batch_size, *self.dim_input))  # Array de numpy con zeros de tama??o
        X2 = np.empty((self.batch_size, * self.dim_input2))
        y = np.empty((self.batch_size, *self.dim_oput))
        # Generate data
        for i, file_name in enumerate(images_names):

            X[i,] = Input_image_jpg(self.PATH + '/Images/' + file_name)
            X2[i,] = Input_image_class(self.PATH + '/depth/' + file_name[:-4]+'.mat',self.dim_input2[2])
            y[i,] = Oput_image_class(self.PATH + '/Labels13/' + file_name[:-4]+'.mat',self.dim_oput[2])
            #y[i,] = Input_image_class(self.PATH + '/depth/' + file_name[:-4] + '.mat', self.dim_oput[2])
        return (X,X2), y




def Build_data_set2(IMG_WIDTH,IMG_HEIGHT,L_imput,L_ouput,CLASS,BATCH_SIZE,PATH,split_v,ty):

  # Random split
  data_dir_list = os.listdir(PATH+'/Images')
  N = len(data_dir_list)
  train_df = pd.DataFrame(columns=['inimg'])
  test_df = pd.DataFrame(columns=['inimg'])
  randurls = np.copy(data_dir_list)
  train_n = round(N * split_v)
  np.random.shuffle(randurls)
  tr_urls = randurls[:train_n]
  ts_urls = randurls[train_n:N]
  for i in tr_urls:
      train_df = train_df.append({'inimg': i}, ignore_index=True)
  for i in ts_urls:
      test_df = test_df.append({'inimg': i}, ignore_index=True)

  params = {'dim_input': (IMG_WIDTH, IMG_HEIGHT, L_imput),
            'dim_input2': (IMG_WIDTH, IMG_HEIGHT, L_ouput),
            'dim_oput': (IMG_WIDTH, IMG_HEIGHT, CLASS),
            'batch_size': BATCH_SIZE,
            'PATH': PATH,
            'shuffle': True,
            'ty':ty}


  partition_Train = load_sambles(test_df)
  partition_Test = load_sambles(train_df)

  train_generator = DataGenerator2(partition_Train, **params)
  test_generator = DataGenerator2(partition_Test, **params)



  train_dataset = tf.data.Dataset.from_generator( lambda: train_generator,
    output_types=((tf.float32, tf.float32), tf.float32),
     output_shapes=(((BATCH_SIZE, IMG_WIDTH,IMG_HEIGHT,L_imput), (BATCH_SIZE, IMG_WIDTH,IMG_HEIGHT,L_ouput)), (BATCH_SIZE, IMG_WIDTH,IMG_HEIGHT,CLASS)))

  test_dataset = tf.data.Dataset.from_generator( lambda: test_generator,
      output_types=((tf.float32, tf.float32), tf.float32),
      output_shapes=(((BATCH_SIZE, IMG_WIDTH, IMG_HEIGHT, L_imput), (BATCH_SIZE, IMG_WIDTH, IMG_HEIGHT, L_ouput)), (BATCH_SIZE, IMG_WIDTH, IMG_HEIGHT, CLASS)))

  return train_dataset,test_dataset

