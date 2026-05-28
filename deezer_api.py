import requests
import re
DEEZER_SEARCH_URL = "https://api.deezer.com/search"

def clean_title(title):
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(r"\(.*?\)", "", title)
    return title.strip()
def clean_artist(artist):
    artist = re.split(r" featuring | ft\. | feat\. | & ", artist, flags=re.IGNORECASE)[0]
    return artist.strip()

def get_deezer_preview(title, artist=None):
    cleaned_title = clean_title(title)
    cleaned_artist = clean_artist(artist) if artist else None
    query = cleaned_title
    if cleaned_artist:
        query = f"{cleaned_artist} {cleaned_title}"

    params = {
        "q": query,
        "limit": 1
    }
    params = {
        "q": query,
        "limit": 1
    }
    try:
        response = requests.get(DEEZER_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("data", [])
        if not items:
            return {
                "preview_url": None,
                "deezer_url": None,
                "album_image": None
            }
        track = items[0]
        return {
            "preview_url": track.get("preview"),
            "deezer_url": track.get("link"),
            "album_image": track.get("album", {}).get("cover_medium")
        }
    except requests.exceptions.RequestException as error:
        print("Deezer preview lookup failed:", error)
        return {
            "preview_url": None,
            "deezer_url": None,
            "album_image": None
        }
def add_deezer_preview(song):
    preview_data = get_deezer_preview(
        title=song.get("title"),
        artist=song.get("artist")
    )
    return {
        **song,
        **preview_data
    }
if __name__ == "__main__":
    result = get_deezer_preview("Clarity", "Zedd")
    print(result)