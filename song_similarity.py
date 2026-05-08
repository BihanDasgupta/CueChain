def compare_songs(a,b):
    bpm_diff = abs(a["bpm"] - b["bpm"])/20
    year_diff = abs(a["year"] - b["year"])/50
    genre_diff = 0
    genre_fam = 0
    if a["genre"] == b["genre"]:
        genre_diff = 1
    else:
        pass
    if a["genre"].split()[0] == b["genre"].split()[0]:
        genre_fam = 1
    else:
        pass
    return [bpm_diff,year_diff,genre_diff,genre_fam]

def make_labels(a,b):
    bpm_similarity = abs(a["bpm"] - b["bpm"]) <= 10
    genre_similarity = a["genre"] == b["genre"]
    genre_fam_similarity = a["genre"].split()[0] == b["genre"].split()[0]
    if bpm_similarity and (genre_fam_similarity or genre_similarity):
        return 1
    else:
        return 0

