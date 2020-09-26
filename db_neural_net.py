# from Space.space import *

import pandas as pd
import numpy as np
from keras.layers import Dense
from keras.models import Sequential, load_model
from keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
# import tensorflow as tf
from helpers.build_db import get_corners, next_group
from sklearn.preprocessing import scale
from keras.optimizers import Adam, SGD


# ### Print Number of GPUs Available ###
# print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
# print(tf.config.list_physical_devices('GPU'))  # print list of GPUs
# print(tf.config.list_physical_devices())    # print list of all devices (GPU and CPU)

# for i in range(20):
#     print('\n')

# ### Data Setup ###

"""
Notes:
1.  There appears to be a change in the player data for years after 1996
"""
corners_data, features_final, targets_final = get_corners(1999, 2017, min_games=48)
a = next_group(corners_data)
print(corners_data.info())
print(corners_data.head(51))
# print(features_final.head())


# df = features_final[:]

# df['Height(in)'] = scale(df['Height(in)'])      # "Center to the mean and component wise scale to unit variance."
# df['Weight(lbs)'] = scale(df['Weight(lbs)'])    #
# df['40 yard'] = scale(df['40 yard'])            #
# df['Bench press'] = scale(df['Bench press'])    #
# df['Vert leap'] = scale(df['Vert leap'])        #
# df['Broad jump'] = scale(df['Broad jump'])      #
# df['Shuttle'] = scale(df['Shuttle'])            #

print(features_final.head())

df_targets_final = pd.get_dummies(targets_final)

print(df_targets_final.head())

features = features_final.values                # Taking just the values of the dataframe, as an array
target = df_targets_final.values    # ...


# ########################## Make and fit the model ##################################

n_cols = features.shape[1]        # The number of features (columns) in the data matrix
model = Sequential()
optimizer = Adam(lr=1e-2)
# optimizer = SGD(lr=1e-3)  # default is 1e-4
#            'tanh',
#            'elu',   - best so far, suspect data requires neuron to allowed to be negative
#            'sigmoid',
#            'relu'
activation1 = 'tanh'
activation2 = 'relu'
activation3 = 'softmax'
activation4 ='elu'
# model.add(Dense(1024, activation=activation, input_shape=(n_cols,)))
model.add(Dense(256, activation=activation4, input_shape=(n_cols,)))  # best so far
# model.add(Dense(128, activation=activation))
# model.add(Dense(32, activation=activation))
# model.add(Dense(64, activation=activation))
model.add(Dense(16, activation=activation4))  #
model.add(Dense(4, activation=activation3))
#
#                       'adam' 'sgd' optimizer
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

filepath = "keras_model_weights\\weights_best_classification.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='val_accuracy',  # 'accuracy'
                             verbose=1,
                             save_best_only=True,
                             mode='max')    # min for loss functions, max for optimizations

early_stopping_monitor = EarlyStopping(patience=500)  # runs without improvement before stopping
callbacks_list = [checkpoint, early_stopping_monitor]  # list of tasks to do before next run
history = model.fit(features, target,
                    validation_split=.3,        # split data into .7 train, .3 test each run
                    epochs=2500,                # do this many runs unless stop early
                    callbacks=callbacks_list)   # after each run do this list of things, defined above


# ############################## Predictions vs Actual #######################################

best = pd.Series(history.history['val_accuracy']).idxmax()
print(np.array(history.history['val_accuracy']).max())

# 2
print('')
print('train accuracy',history.history['accuracy'][best])
print('test accuracy',history.history['val_accuracy'][best])
print('\n')

my_model = load_model(filepath)

predictions = my_model.predict(features)

result_dict = {'prediction': list(predictions),
               'actual': list(target)}
df_result = pd.DataFrame(result_dict)

df_result['Name'] = corners_data['Name']
df_result['Draft Year'] = corners_data['Draft Year']
df_result['Games'] = corners_data['Games']
df_result['Draft Pos'] = corners_data['Draft Pos']

print(df_result.head(50))
