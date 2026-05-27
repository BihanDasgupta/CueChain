import numpy as np
from song_similarity import compare_songs
import tensorflow as tf

model = tf.keras.models.load_model("transition_model.keras")
def recommend_songs(curr_song, songs, model, top_n = 5):
    recommendations = []
    for option in songs:
        if option["title"] == curr_song["title"]:
            continue
        features = np.array([compare_songs(curr_song, option)],dtype=float)
        score = model.predict(features,verbose = 0)[0][0]
        recommendations.append({"artist": option["artist"],
        "title": option["title"],
        "bpm": option["bpm"],
        "year": option["year"],
        "genre": option["genre"],
        "score": float(score)})
    recommendations.sort(key = lambda item: item["score"],reverse = True)
    return recommendations[:top_n]
def explain_recommendation(a,b):
    reasons = []
    bpm_diff = abs(a["bpm"]-b["bpm"])
    if bpm_diff<=5:
        reasons.append("similar bpm")
    else:
        reasons.append("large bpm difference")
    if a["genre"] == b["genre"]:
        reasons.append("same genre")
    elif a["genre"].split()[0] == b["genre"].split()[0]:
        reasons.append("same genre family")
    else:
        reasons.append("different genres")
    return ", ".join(reasons)

