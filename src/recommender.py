import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional

# Points each rule can add to a song's score.
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

NUMERIC_FIELDS = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    genre_prefs / mood_prefs map each genre or mood to its share of the
    user's listening history, e.g. {"pop": 0.5, "lofi": 0.3, "rock": 0.2}.
    When they're empty, favorite_genre / favorite_mood are used instead.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    genre_prefs: Dict[str, float] = field(default_factory=dict)
    mood_prefs: Dict[str, float] = field(default_factory=dict)


def preference_strength(value: str, prefs: Dict[str, float], favorite: Optional[str]) -> float:
    """
    How much the user likes `value`, from 0 to 1, relative to their top choice.

    With prefs {"pop": 0.5, "rock": 0.2}: pop -> 1.0, rock -> 0.4, jazz -> 0.0.
    With no prefs, falls back to 1.0 for the single favorite and 0.0 otherwise.
    """
    if prefs:
        top = max(prefs.values())
        return prefs.get(value, 0.0) / top if top > 0 else 0.0
    return 1.0 if value == favorite else 0.0


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Stores the catalog of songs to recommend from."""
        self.songs = songs

    @staticmethod
    def _user_prefs(user: UserProfile) -> Dict:
        """Converts a UserProfile into the user_prefs dict that score_song expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "genre_prefs": user.genre_prefs,
            "mood_prefs": user.mood_prefs,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for the user, highest score first."""
        prefs = self._user_prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda s: (-score_song(prefs, asdict(s))[0], s.id),
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a readable string with the song's score and the reasons behind it."""
        score, reasons = score_song(self._user_prefs(user), asdict(song))
        if not reasons:
            return f"Score {score:.2f}: no strong matches with your preferences"
        return f"Score {score:.2f}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for name in NUMERIC_FIELDS:
                row[name] = float(row[name])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs keys: "genre", "mood", "energy", and optionally
    "likes_acoustic", "genre_prefs", "mood_prefs".
    """
    score = 0.0
    reasons = []

    genre = preference_strength(song["genre"], user_prefs.get("genre_prefs") or {}, user_prefs.get("genre"))
    if genre > 0:
        points = GENRE_WEIGHT * genre
        score += points
        reasons.append(f"genre {song['genre']} (+{points:.2f})")

    mood = preference_strength(song["mood"], user_prefs.get("mood_prefs") or {}, user_prefs.get("mood"))
    if mood > 0:
        points = MOOD_WEIGHT * mood
        score += points
        reasons.append(f"mood {song['mood']} (+{points:.2f})")

    # Closeness, not raw value: full points when the song's energy equals the target.
    if user_prefs.get("energy") is not None:
        points = ENERGY_WEIGHT * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += points
        reasons.append(f"energy {song['energy']:.2f} close to target (+{points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        if (likes_acoustic and song["acousticness"] > 0.6) or (not likes_acoustic and song["acousticness"] < 0.4):
            score += ACOUSTIC_WEIGHT
            reasons.append(f"{'acoustic' if likes_acoustic else 'non-acoustic'} sound (+{ACOUSTIC_WEIGHT:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))
    # Highest score first; ties broken by id so the order is always the same.
    scored.sort(key=lambda item: (-item[1], item[0]["id"]))
    return scored[:k]
