from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import scipy.misc
from PIL import Image
import imageio
import os
import sys
import re
import glob
from utils import *

def center_crop(img, mask, random_crop_size):
    height, width = img.shape[0], img.shape[1]
    dy, dx = random_crop_size
    y = (height - dy)//2
    x = (width - dx)//2
    return img[y:(y+dy), x:(x+dx), :], mask[y:(y+dy), x:(x+dx), :]

def random_crop(img, mask, random_crop_size):
    # Note: image_data_format is 'channel_last'
    # assert img.shape[2] == 3
    height, width = img.shape[0], img.shape[1]
    dy, dx = random_crop_size
    x = np.random.randint(0, width - dx + 1)
    y = np.random.randint(0, height - dy + 1)
    return img[y:(y+dy), x:(x+dx), :], mask[y:(y+dy), x:(x+dx), :]

def crop_generator(batches, crop_length, random=True): # change to enable x and y together
    """Take as input a Keras ImageGen (Iterator) and generate random
    crops from the image batches generated by the original iterator.
    """
    while True:
        batch_x, batch_y = next(batches)
        batch_crop_x = np.zeros((batch_x.shape[0], crop_length, crop_length, 3))
        batch_crop_y = np.zeros((batch_y.shape[0], crop_length, crop_length, 2))
        for i in range(batch_x.shape[0]):
            if random:
                batch_crop_x[i], batch_crop_y[i] = random_crop(batch_x[i], batch_y[i], (crop_length, crop_length))
            else:
                batch_crop_x[i], batch_crop_y[i] = center_crop(batch_x[i], batch_y[i], (crop_length, crop_length))
        yield (batch_crop_x, batch_crop_y)     
        
        
def squeeze(batches): # change to enable x and y together
    while True:
        batch_x, batch_y = next(batches)
        batch_y = batch_y[:,:,:,0]
        
        yield (batch_x, batch_y) 
        
def trainGen(train_x, train_y, batch_size):
    '''
    can generate image and mask at the same time
    use the same seed for image_datagen and mask_datagen to ensure the transformation for image and mask is the same
    if you want to visualize the results of generator, set save_to_dir = "your path"
    '''
    #has rescaled when loading the data
    if train_y.ndim != 4:
        train_y = np.expand_dims(train_y, axis=-1)
        print('expand dims',train_y.shape)
    train_x = train_x * 1./255
    x_gen_args = dict(
#                     rescale = 1./255,
#                     rotation_range=0.2,
#                     width_shift_range=0.05,
#                     height_shift_range=0.05,
#                     shear_range=0.05,
#                     zoom_range=0.05,
                    horizontal_flip=True,
                    vertical_flip=True,
                    fill_mode='wrap'
    )
    
    y_gen_args = dict(
#                     rotation_range=0.2,
#                     width_shift_range=0.05,
#                     height_shift_range=0.05,
#                     shear_range=0.05,
#                     zoom_range=0.05,
                    horizontal_flip=True,
                    vertical_flip=True,
                    fill_mode='wrap'
    )
    
    img_datagen = ImageDataGenerator(**x_gen_args)
    mask_datagen = ImageDataGenerator(**y_gen_args)
    
    img_datagen.fit(train_x)
    mask_datagen.fit(train_y)

    seed = 2018
    img_gen = img_datagen.flow(train_x, seed = seed, batch_size=batch_size, shuffle=True)#shuffling
    mask_gen = mask_datagen.flow(train_y, seed = seed, batch_size=batch_size, shuffle=True)
    
    train_gen = zip(img_gen, mask_gen)
    train_gen = squeeze(train_gen) # squeeze

    return train_gen

def testGen(val_x, val_y, batch_size):
# val_gen
    img_datagen = ImageDataGenerator(rescale = 1./255)
    mask_datagen = ImageDataGenerator()
    
    img_datagen.fit(val_x)
    mask_datagen.fit(val_y)
    
    seed = 20
    img_gen = img_datagen.flow(val_x, seed=seed, batch_size=batch_size, shuffle=False)
    mask_gen = mask_datagen.flow(val_y, seed=seed, batch_size=batch_size, shuffle=False)
    val_gen = zip(img_gen, mask_gen)    
#     val_crops = crop_generator(val_gen, 224, random=False)    
    return val_gen


