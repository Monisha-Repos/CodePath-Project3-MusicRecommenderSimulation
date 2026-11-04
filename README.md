# 🎵 Music Recommender Simulation

## Project Summary

**TuneMatch 1.0** is a small content-based music recommender that runs in the terminal. It loads a catalog of 20 songs from `data/songs.csv`, scores every song against a user's taste profile (genre, mood, energy and acoustic preference), and prints the top 5 matches with the reasons behind each score.

The user's taste is stored as listening-history percentages (for example, 50% pop, 30% lofi, 20% rock), so second and third favorite genres still get partial credit. I tested it with 8 user profiles, including edge cases meant to trick it, and documented its strengths, biases and limits in the [Model Card](model_card.md).

---

## How The System Works

Real-world apps like Spotify and YouTube mix two approaches. **Collaborative filtering** uses other people's behavior: if listeners who like the songs you like also like song X, you'll probably like X too. It learns from likes, skips, replays and playlists across millions of users. **Content-based filtering** uses the songs' own attributes, like genre, mood, energy and tempo, and recommends songs similar to what you already enjoy. Big platforms combine both, plus context like time of day.

My version is **content-based only**. It has no other users, just song attributes and one user's taste. It prioritizes **genre** first, then **mood**, then how close a song's **energy** is to what the user wants, with a small bonus for matching their **acoustic** preference.

### Song features

Each song stores everything in the CSV: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`.

The scoring uses four of them:

- `genre` (text, e.g. "pop")
- `mood` (text, e.g. "happy")
- `energy` (0 to 1)
- `acousticness` (0 to 1)

I skipped tempo and danceability because in this data they mostly rise and fall with energy, so they would count the same thing twice. `title` and `artist` are only for display.

### UserProfile

| Field | Type | Example |
|---|---|---|
| `genre_prefs` | dict of genre → share of listening history | `{"pop": 0.5, "lofi": 0.3, "rock": 0.2}` |
| `mood_prefs` | dict of mood → share of listening history | `{"happy": 0.6, "chill": 0.4}` |
| `target_energy` | number, 0 to 1 | `0.8` |
| `likes_acoustic` | yes/no | `False` |
| `favorite_genre` | text, used only if `genre_prefs` is empty | `"pop"` |
| `favorite_mood` | text, used only if `mood_prefs` is empty | `"happy"` |

`favorite_genre` and `favorite_mood` are there because the starter tests create users with them.

### Algorithm Recipe

**Scoring Rule (one song).** A song earns points for how well it fits the user:

| Rule | Points |
|---|---|
| **Genre** | Up to +2.0. The user's most-listened genre gets the full 2 points; other genres get points in proportion. If pop is 50% and lofi is 30%, a lofi song gets 2 × 30/50 = 1.2. Genres they never listen to get 0. |
| **Mood** | Up to +1.0, scored the same way as genre. |
| **Energy** | Up to +1.0: `1 - abs(song energy - target energy)`. The closer, the more points. |
| **Acoustic** | +0.5 if it matches their preference (acousticness above 0.6 for users who like acoustic, below 0.4 for users who don't). |

The highest possible score is 4.5. Each rule that adds points also adds a reason, like `genre pop (+2.00)`, so every recommendation explains itself.

**Ranking Rule (the list).** Score every song, sort from highest to lowest (ties broken by song id), and show the top 5.

```
User profile ─┐
              ├─► score_song() for every song ─► sort by score ─► top 5 + reasons
songs.csv ────┘
```

### Expected biases

- **Genre comes first:** a song in the user's favorite genre usually beats a better mood match from another genre.
- **Filter bubble:** genres and moods the user hasn't listened to score 0, so it rarely suggests anything new.
- **Exact labels:** "relaxed" and "chill" count as different moods, so close matches miss out.
- **Uneven catalog:** lofi has 3 songs while most genres have 1, so some users get more good options than others.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default pop/happy profile (the app prints 7 more profiles after this one):

```
Loaded songs: 20

============================================================
  Top Recommendations: Default Pop/Happy
============================================================
  Genres: pop 50%, lofi 30%, rock 20%
  Moods:  happy 60%, chill 40%
  Target energy: 0.8
------------------------------------------------------------

1. Sunrise City by Neon Echo
   pop / happy   Score: 3.98
     - genre pop (+2.00)
     - mood happy (+1.00)
     - energy 0.82 close to target (+0.98)

2. Gym Hero by Max Pulse
   pop / intense   Score: 2.87
     - genre pop (+2.00)
     - energy 0.93 close to target (+0.87)

3. Midnight Coding by LoRoom
   lofi / chill   Score: 2.49
     - genre lofi (+1.20)
     - mood chill (+0.67)
     - energy 0.42 close to target (+0.62)

4. Library Rain by Paper Lanterns
   lofi / chill   Score: 2.42
     - genre lofi (+1.20)
     - mood chill (+0.67)
     - energy 0.35 close to target (+0.55)

5. Rooftop Lights by Indigo Parade
   indie pop / happy   Score: 1.96
     - mood happy (+1.00)
     - energy 0.76 close to target (+0.96)
```

The output for all 8 profiles is in the [Model Card](model_card.md#7-evaluation).

---

## Experiments You Tried

- **8 user profiles:** 3 typical listeners (High-Energy Pop, Chill Lofi, Deep Intense Rock) and 5 edge cases (Sad but Hyped, Ghost Genre, Acoustic Headbanger, Fence Sitter, plus the default). Typical profiles got a sensible #1. Edge cases exposed odd picks, like a country song recommended to a metal fan because of the acoustic bonus.
- **Weight shift (energy doubled to 2.0, genre halved to 1.0):** the #1 song didn't change for any profile. Some lists improved; for example, *Rooftop Lights* moved up for the pop fan. Others got worse, with more high-energy filler for the rock fan. The results were mostly different, not more accurate, so I kept the original weights.

Details are in the [Model Card](model_card.md#7-evaluation).

---

## Limitations and Risks

- It only works on a tiny catalog of 20 songs, and most genres have just 1 song.
- High-energy songs fill the gaps for everyone: *Gym Hero* appeared in the top 5 for 6 of the 8 profiles.
- It never suggests genres or moods the user hasn't listened to, which creates a filter bubble.
- Genre and mood must match exactly, so "relaxed" gets no credit for a "chill" listener.
- It ignores lyrics, language, valence (happy vs. sad sound) and how taste changes over time.

More in the [Model Card](model_card.md#6-limitations-and-bias).

---

## Reflection

Read the full [**Model Card**](model_card.md), including my personal reflection.

Building this showed me that a recommendation is just math. Each song gets turned into a few numbers, the user's taste gets turned into a few targets, and a scoring rule measures how close they are. Then everything is sorted. Even so, the results often feel personal: the lofi fan gets calm, acoustic study music, and the rock fan gets loud guitar. Small changes matter, though; changing two weights reshuffled several users' top 5.

Bias shows up in quiet ways. The system only rewards what the user already listens to, so it keeps them in a bubble. It also leans on whatever the catalog has the most of: with lots of loud, high-energy songs, those songs keep getting recommended to people who didn't ask for them. And because it trusts labels, a song tagged slightly differently ("relaxed" vs. "chill") gets ignored. In a real app with millions of users, the same patterns could decide which artists get heard at all.
