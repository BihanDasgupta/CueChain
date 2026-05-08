"""
Basic tensorflow model for song transition decision ranking.
This model compares BPM, genre, and year features and predicts if the next song would be the
next best transition.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

x = []
y = []

for a in songs:
    for b in songs:
        if a["title"]!=b["title"]:
            x.append(compare_songs(a,b))
            y.append(make_labels(a,b))
x = np.array(x,dtype = float)
y = np.array(y,dtype = float)

model = models.Sequential([tf.keras.Input(shape=(4,)),layers.Dense(8,"relu", (4,)),
                           layers.Dense(4,"relu"),
                           layers.Dense(1,"sigmoid")])
model.compile("adam","binary_crossentropy",metrics=["accuracy"])
model.fit(x,y,epochs = 50,verbose=0)
loss,accuracy = model.evaluate(x,y,verbose=0)
print("training accuracy:",round(accuracy,3))