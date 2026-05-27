"""
Basic tensorflow model for song transition decision ranking.
This model compares BPM, genre, and year features and predicts if the next song would be the
next best transition.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from songs import songs
from song_similarity import compare_songs, make_labels
x = []
y = []

for a in songs:
    for b in songs:
        if a["title"] != b["title"]:
            x.append(compare_songs(a, b))
            y.append(make_labels(a, b))

x = np.array(x, dtype=float)
y = np.array(y, dtype=float)

indices = np.arange(len(x))
np.random.shuffle(indices)

x = x[indices]
y = y[indices]

split_index = int(0.8 * len(x))

x_train = x[:split_index]
y_train = y[:split_index]

x_test = x[split_index:]
y_test = y[split_index:]

model = models.Sequential([
    tf.keras.Input(shape=(4,)),
    layers.Dense(8, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.fit(x_train, y_train, epochs=5, verbose=1)

train_loss, train_accuracy = model.evaluate(x_train, y_train, verbose=1)
test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=1)

model.save("transition_model.keras")

