import requests
from bs4 import BeautifulSoup
from pprint import pformat
from time import sleep

BASE_URL = "https://cs.uwaterloo.ca/~dtompkin/music/bpm/{bpm}.html"
START_BPM = 100
END_BPM = 170
MAX_SONGS_PER_BPM = 20
headers = {"User-Agent": "Mozilla/5.0"}
songs = []
def scrape_bpm_page(bpm_number):
    url = BASE_URL.format(bpm=bpm_number)
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    page_songs = []
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        values = [cell.get_text(" ", strip=True) for cell in cells]
        values = [v for v in values if v]
        if len(values) < 6:
            continue
        try:
            scraped_bpm = float(values[3])
            year = int(values[4])
        except ValueError:
            continue
        page_songs.append({
            "artist": values[0],
            "title": values[1],
            "bpm": scraped_bpm,
            "year": year,
            "genre": values[5],
        })
        if len(page_songs) >= MAX_SONGS_PER_BPM:
            break
    return page_songs
for bpm_number in range(START_BPM, END_BPM + 1):
    try:
        bpm_songs = scrape_bpm_page(bpm_number)
        songs.extend(bpm_songs)
        print(f"BPM {bpm_number}: scraped {len(bpm_songs)} songs")
        sleep(0.25)
    except requests.RequestException as error:
        print(f"BPM {bpm_number}: skipped because of request error: {error}")
with open("songs.py", "w", encoding="utf-8") as f:
    f.write("songs = ")
    f.write(pformat(songs, sort_dicts=False, width=100))
    f.write("\n")