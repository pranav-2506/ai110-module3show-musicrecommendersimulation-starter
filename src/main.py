"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

import sys
import os

# Ensure 'src/' is on the path so 'recommender' can be imported
# regardless of how this module is invoked.
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Default taste profile — edit these values to try different listeners
    user_prefs = {
        "genre":   "pop",
        "mood":    "happy",
        "energy":  0.80,
        "valence": 0.80,
    }

    k = 5
    recommendations = recommend_songs(user_prefs, songs, k=k)

    # ── Header ──────────────────────────────────────────────────────────────
    print()
    print("=" * 52)
    print("  Music Recommender — Top Picks")
    print("=" * 52)
    print(f"  Profile : genre={user_prefs['genre']}  "
          f"mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}")
    print("-" * 52)

    # ── Results ─────────────────────────────────────────────────────────────
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f} / 10.5")
        print(f"       Why   : {explanation}")
        print()

    print("=" * 52)


if __name__ == "__main__":
    main()
