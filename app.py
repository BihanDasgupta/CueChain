import random
from difflib import get_close_matches

from flask import Flask, jsonify, request
from flask_cors import CORS

from recommender import model, recommend_songs
from songs import songs
from store_transitions import store_transition
from soundchart_api import get_song


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

transition_memory = {}
THRESHOLD = 0.85
CANDIDATE_POOL_SIZE = 10
RECOMMENDATION_COUNT = 3


def find_song(title):
    search_title = title.strip().lower()
    title_lookup = {song["title"].lower(): song for song in songs}

    if search_title in title_lookup:
        return title_lookup[search_title]

    for song in songs:
        if search_title in song["title"].lower():
            return song

    return None


def weighted_sample_recommendations(recommendations, count):
    candidates = list(recommendations)
    selected = []

    while candidates and len(selected) < count:
        weights = [max(item["score"], 0.0001) ** 4 for item in candidates]
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        selected.append(chosen)
        candidates.remove(chosen)

    return selected


def prepare_transition_edge(curr_song, recommendation):
    stored_on_chain = False
    signature = None

    if recommendation["score"] > THRESHOLD:
        transition = {
            "songA": curr_song["title"],
            "songB": recommendation["title"],
            "score": recommendation["score"],
        }

        try:
            signature = str(store_transition(transition))
            stored_on_chain = True
        except Exception as error:
            print(f"Failed to store transition on Solana: {error}")

    return {
        "from_song": curr_song["title"],
        "title": recommendation["title"],
        "artist": recommendation["artist"],
        "genre": recommendation["genre"],
        "bpm": recommendation["bpm"],
        "score": recommendation["score"],
        "stored_on_chain": stored_on_chain,
        "signature": signature,
    }


@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response, 200

    data = request.get_json(silent=True) or {}
    song_title = data.get("song", "").strip()

    if not song_title:
        return jsonify({"error": "Song title is required."}), 400

    curr_song = get_song(
    title=song_title,
    songs=songs
    )
    if not curr_song:
        return jsonify({"error": f"Song not found: {song_title}"}), 404

    memory_key = curr_song["title"].lower()
    if memory_key in transition_memory:
        memory_sample = weighted_sample_recommendations(
            transition_memory[memory_key],
            RECOMMENDATION_COUNT,
        )
        remembered_recommendations = [
            {
                **recommendation,
                "retrieved_from_memory": True,
                "newly_generated": False,
            }
            for recommendation in memory_sample
        ]

        return jsonify({
            "retrieved_from_memory": True,
            "song": curr_song["title"],
            "recommendations": remembered_recommendations,
        })

    raw_recommendations = recommend_songs(
        curr_song,
        songs,
        model,
        top_n=CANDIDATE_POOL_SIZE,
    )
    discovered_edges = [
        prepare_transition_edge(curr_song, recommendation)
        for recommendation in raw_recommendations
    ]

    # Transition memory represents discovered graph edges that can be reused
    # without recomputing ML scores or writing duplicate Solana transactions.
    transition_memory[memory_key] = discovered_edges
    recommendations = [
        {
            **recommendation,
            "retrieved_from_memory": False,
            "newly_generated": True,
        }
        for recommendation in weighted_sample_recommendations(
            discovered_edges,
            RECOMMENDATION_COUNT,
        )
    ]

    return jsonify({
        "retrieved_from_memory": False,
        "song": curr_song["title"],
        "recommendations": recommendations,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)