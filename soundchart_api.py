import os
import requests


BASE_URL = "https://customer.api.soundcharts.com"
def get_headers():
    app_id = os.getenv("SOUNDCHARTS_APP_ID")
    api_key = os.getenv("SOUNDCHARTS_API_KEY")

    if not app_id or not api_key:
        raise ValueError(
            "Missing Soundcharts credentials. "
            "Set SOUNDCHARTS_APP_ID and SOUNDCHARTS_API_KEY first."
        )
    return {
        "x-app-id": app_id,
        "x-api-key": api_key
    }
def find_local_song(title, songs, artist=None):
    title = title.lower().strip()
    artist = artist.lower().strip() if artist else None
    for song in songs:
        song_title = song["title"].lower().strip()
        song_artist = song["artist"].lower().strip()
        if artist:
            if song_title == title and song_artist == artist:
                return song
        else:
            if song_title == title:
                return song

    return None
def search_soundcharts_song(title, artist=None):
    headers = get_headers()
    search_term = title
    if artist:
        search_term = f"{title} {artist}"
    url = f"{BASE_URL}/api/v2/song/search/{search_term}"
    params = {
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    items = data.get("items") or data.get("songs") or data.get("data")
    if not items:
        raise ValueError(f"No Soundcharts results found for: {search_term}")
    first_song = items[0]
    song_uuid = (
        first_song.get("uuid")
        or first_song.get("songUuid")
        or first_song.get("id")
    )
    if not song_uuid:
        raise ValueError(
            "Could not find UUID in Soundcharts search result. "
            "Print the response JSON and adjust search_soundcharts_song()."
        )
    return song_uuid

def get_soundcharts_metadata(song_uuid):
    headers = get_headers()
    url = f"{BASE_URL}/api/v2.25/song/{song_uuid}"
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()

def convert_to_song_format(metadata):
    song_data = metadata.get("object", metadata.get("song", metadata))
    title = (
        song_data.get("name")
        or song_data.get("title")
        or "Unknown Title"
    )
    artists = song_data.get("mainArtists") or song_data.get("artists", [])

    if isinstance(artists, list) and len(artists) > 0:
        if isinstance(artists[0], dict):
            artist = artists[0].get("name", "Unknown Artist")
        else:
            artist = str(artists[0])
    else:
        artist = (
            song_data.get("creditName")
            or song_data.get("artistName")
            or song_data.get("artist")
            or "Unknown Artist"
        )
    release_date = (
        song_data.get("releaseDate")
        or song_data.get("release_date")
        or ""
    )
    try:
        year = int(str(release_date)[:4])
    except ValueError:
        year = 0
    genres = song_data.get("genres", [])
    if isinstance(genres, list) and len(genres) > 0:
        first_genre = genres[0]

        if isinstance(first_genre, dict):
            genre = first_genre.get("root", "Unknown")
        else:
            genre = str(first_genre)
    else:
        genre = "Unknown"
    audio_features = (
        song_data.get("audio")
        or song_data.get("audioFeatures")
        or song_data.get("audio_features")
        or metadata.get("audio")
        or metadata.get("audioFeatures")
        or metadata.get("audio_features")
        or {}
    )
    bpm = (
        audio_features.get("tempo")
        or audio_features.get("bpm")
        or 0.0
    )
    return {
        "artist": artist,
        "title": title,
        "bpm": float(bpm),
        "year": year,
        "genre": genre,
        "energy": audio_features.get("energy"),
        "danceability": audio_features.get("danceability"),
        "valence": audio_features.get("valence"),
        "loudness": audio_features.get("loudness"),
        "key": audio_features.get("key"),
        "mode": audio_features.get("mode")
    }
def get_song(title, songs, artist=None):
    local_song = find_local_song(title, songs, artist)
    if local_song:
        print("Found song in local songs.py dataset.")
        return local_song
    print("Song not found locally. Calling Soundcharts API.")
    try:
        song_uuid = search_soundcharts_song(title, artist)
        metadata = get_soundcharts_metadata(song_uuid)
        return convert_to_song_format(metadata)
    except requests.exceptions.HTTPError as error:
        status_code = error.response.status_code
        if status_code == 403:
            print("Soundcharts returned 403. This endpoint may not be available on the current API plan.")
            print("Falling back gracefully. No API song returned.")
            return None
        if status_code == 404:
            print("Song not found in Soundcharts.")
            return None
        print(f"Soundcharts HTTP error: {status_code}")
        return None
    except requests.exceptions.RequestException as error:
        print("Request error while calling Soundcharts:", error)
        return None
    except ValueError as error:
        print("Could not parse Soundcharts response:", error)
        return None

if __name__ == "__main__":
    from songs import songs
    searched_song = get_song(
        title="Clarity",
        songs=songs,
        artist="Zedd"
    )
    if searched_song is None:
        print("Song could not be found locally or through Soundcharts.")
    else:
        print("Song found:")
        print(searched_song)