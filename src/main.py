"""
Command line runner for the Music Recommender Simulation.

Runs the recommender for several user profiles and prints the top 5 for each.
"""

try:
    from src.recommender import load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs  # python src/main.py


# genre_prefs / mood_prefs are shares of the user's listening history;
# each is scored relative to the user's top choice.
PROFILES = {
    # Starter example profile (shown in the README sample output)
    "Default Pop/Happy": {
        "genre": "pop", "mood": "happy", "energy": 0.8,
        "genre_prefs": {"pop": 0.5, "lofi": 0.3, "rock": 0.2},
        "mood_prefs": {"happy": 0.6, "chill": 0.4},
    },

    # --- Typical listeners ---
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
        "genre_prefs": {"lofi": 0.60, "jazz": 0.25, "ambient": 0.15},
        "mood_prefs": {"chill": 0.70, "focused": 0.30},
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False,
        "genre_prefs": {"rock": 0.60, "metal": 0.40},
        "mood_prefs": {"intense": 0.60, "angry": 0.40},
    },

    # --- Edge cases: trying to trick the scoring ---
    # Conflicting: wants high energy but a sad mood (sad songs here are calm).
    "Sad but Hyped": {
        "genre": "blues", "mood": "sad", "energy": 0.9, "likes_acoustic": False,
    },
    # Favorite genre isn't in the catalog at all.
    "Ghost Genre (k-pop)": {
        "genre": "k-pop", "mood": "happy", "energy": 0.7, "likes_acoustic": False,
    },
    # Loves metal, but also wants acoustic sound (no song is both).
    "Acoustic Headbanger": {
        "genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True,
    },
    # Listens to everything equally, middle energy, no acoustic preference.
    "Fence Sitter": {
        "genre": "pop", "mood": "happy", "energy": 0.5,
        "genre_prefs": {"pop": 0.25, "rock": 0.25, "jazz": 0.25, "country": 0.25},
        "mood_prefs": {"happy": 0.5, "sad": 0.5},
    },
}


def main() -> None:
    """Loads the catalog and prints the top 5 songs for every profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Prints each recommendation with its score and the reasons behind it."""
    genres = ", ".join(f"{g} {share:.0%}" for g, share in user_prefs.get("genre_prefs", {}).items())
    moods = ", ".join(f"{m} {share:.0%}" for m, share in user_prefs.get("mood_prefs", {}).items())
    acoustic = user_prefs.get("likes_acoustic")
    print("\n" + "=" * 60)
    print(f"  Top Recommendations: {name}")
    print("=" * 60)
    print(f"  Genres: {genres or user_prefs.get('genre')}")
    print(f"  Moods:  {moods or user_prefs.get('mood')}")
    print(f"  Target energy: {user_prefs.get('energy')}")
    if acoustic is not None:
        print(f"  Likes acoustic: {'yes' if acoustic else 'no'}")
    print("-" * 60)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   {song['genre']} / {song['mood']}   Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"     - {reason}")
    print()


if __name__ == "__main__":
    main()
