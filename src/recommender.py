import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

# BPM range used to normalise tempo to 0-1 for proximity scoring
_BPM_MIN = 60
_BPM_MAX = 168


@dataclass
class Song:
    """Represents a single song and its audio attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a listener's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _proximity(song_val: float, user_val: float) -> float:
    """Return a 0-1 similarity score: 1.0 = identical, 0.0 = maximally different."""
    return 1.0 - abs(song_val - user_val)


# ---------------------------------------------------------------------------
# Step 1: load_songs
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with typed numeric values."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


# ---------------------------------------------------------------------------
# Step 2: score_song
# ---------------------------------------------------------------------------

_DEFAULT_WEIGHTS = {
    "mood":         2.5,
    "genre":        1.5,
    "energy":       3.0,
    "valence":      2.0,
    "tempo":        1.0,
    "acousticness": 0.5,
}


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Dict = None,
) -> Tuple[float, str]:
    """Score one song against user preferences; return (score, explanation string).

    Pass a custom `weights` dict to override any default weight for experiments.
    Default maximum possible score: 10.5
      mood match        +2.5
      genre match       +1.5
      energy proximity  up to +3.0
      valence proximity up to +2.0
      tempo proximity   up to +1.0
      acousticness prox up to +0.5
    """
    w = {**_DEFAULT_WEIGHTS, **(weights or {})}
    score = 0.0
    reasons: List[str] = []

    # Categorical matches
    if song.get("mood") == user_prefs.get("mood"):
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']})")

    if song.get("genre") == user_prefs.get("genre"):
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']})")

    # Numeric proximity features
    if "energy" in user_prefs:
        ep = _proximity(song["energy"], float(user_prefs["energy"])) * w["energy"]
        score += ep
        reasons.append(f"energy proximity (+{ep:.2f})")

    if "valence" in user_prefs:
        vp = _proximity(song["valence"], float(user_prefs["valence"])) * w["valence"]
        score += vp
        reasons.append(f"valence proximity (+{vp:.2f})")

    if "tempo_bpm" in user_prefs:
        song_t = (song["tempo_bpm"] - _BPM_MIN) / (_BPM_MAX - _BPM_MIN)
        user_t = (float(user_prefs["tempo_bpm"]) - _BPM_MIN) / (_BPM_MAX - _BPM_MIN)
        tp = _proximity(song_t, user_t) * w["tempo"]
        score += tp
        reasons.append(f"tempo proximity (+{tp:.2f})")

    if "acousticness" in user_prefs:
        ap = _proximity(song["acousticness"], float(user_prefs["acousticness"])) * w["acousticness"]
        score += ap
        reasons.append(f"acousticness proximity (+{ap:.2f})")

    explanation = ", ".join(reasons) if reasons else "no matching features"
    return score, explanation


# ---------------------------------------------------------------------------
# Step 3: recommend_songs
# ---------------------------------------------------------------------------

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Dict = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, deduplicate by artist, and return the top-k as (song, score, explanation).

    Pass a custom `weights` dict to run experiments without changing default logic.
    Uses sorted() (not .sort()) so the original list is never mutated.
    sorted() returns a brand-new list in the requested order; .sort() would
    reorder the list in place, which could surprise callers that hold a
    reference to the same list.
    """
    scored = [
        (song, *score_song(user_prefs, song, weights=weights))
        for song in songs
    ]

    # sorted() — new list, descending by score
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    results: List[Tuple[Dict, float, str]] = []
    seen_artists: set = set()

    for song, sc, explanation in ranked:
        if song["artist"] not in seen_artists:
            results.append((song, sc, explanation))
            seen_artists.add(song["artist"])
        if len(results) >= k:
            break

    return results


# ---------------------------------------------------------------------------
# OOP wrapper (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP wrapper that scores Song dataclass instances against a UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _profile_to_prefs(self, user: UserProfile) -> Dict:
        """Convert a UserProfile to the user_prefs dict format expected by score_song."""
        return {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "acousticness": 0.85 if user.likes_acoustic else 0.15,
        }

    def _song_to_dict(self, song: Song) -> Dict:
        """Convert a Song dataclass to the plain dict format expected by score_song."""
        return {
            "id":           song.id,
            "title":        song.title,
            "artist":       song.artist,
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "tempo_bpm":    song.tempo_bpm,
            "valence":      song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given user."""
        prefs = self._profile_to_prefs(user)
        scored = [
            (song, score_song(prefs, self._song_to_dict(song))[0])
            for song in self.songs
        ]
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why this song was recommended."""
        prefs = self._profile_to_prefs(user)
        _, explanation = score_song(prefs, self._song_to_dict(song))
        return explanation
