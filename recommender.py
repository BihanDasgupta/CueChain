import numpy as np
from song_similarity import compare_songs
import tensorflow as tf

model = tf.keras.models.load_model("transition_model.keras")
def recommend_songs(curr_song, songs, model, top_n=5):
    candidates = []
    feature_rows = []
    for option in songs:
        if option["title"] == curr_song["title"]:
            continue
        bpm_diff = abs(curr_song["bpm"] - option["bpm"])
        if bpm_diff > 10:
            continue
        candidates.append(option)
        feature_rows.append(compare_songs(curr_song, option))
    if not candidates:
        print("No nearby BPM candidates found. Using full dataset as fallback.")
        for option in songs:
            if option["title"] == curr_song["title"]:
                continue

            candidates.append(option)
            feature_rows.append(compare_songs(curr_song, option))
    features = np.array(feature_rows, dtype=float)
    scores = model.predict(features, verbose=0).flatten()
    recommendations = []
    for option, score in zip(candidates, scores):
        bpm_diff = abs(curr_song["bpm"] - option["bpm"])
        bpm_score = max(0, 1 - (bpm_diff / 10))
        final_score = max(float(score), bpm_score)
        recommendations.append({
            "artist": option["artist"],
            "title": option["title"],
            "bpm": option["bpm"],
            "year": option["year"],
            "genre": option["genre"],
            "score": final_score,
            "songA": curr_song["title"],
            "songB": option["title"],
            "reason": explain_recommendation(curr_song, option)
        })
    recommendations.sort(key=lambda item: item["score"], reverse=True)
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

