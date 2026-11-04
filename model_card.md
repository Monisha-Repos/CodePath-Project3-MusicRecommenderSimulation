# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**TuneMatch 1.0**: a points-based song recommender that matches songs to a listener's taste.

---

## 2. Intended Use  

**Goal:** given a listener's taste, suggest the 5 songs from the catalog they're most likely to enjoy, and explain why each one was picked.

**What it assumes about the user:**

- We know what share of their listening is each genre and mood.
- They want songs near one energy level.
- They either like acoustic music or they don't.
- Their taste stays the same; it doesn't change with time of day or activity.

**Intended use:** classroom exploration. It's for learning how content-based recommenders turn data into rankings, and for seeing where simple scoring rules go wrong.

**Not intended for:**

- Real users or a real music app. The catalog has only 20 made-up songs.
- Judging the quality of a song or artist. A low score only means a poor match for one profile.
- Discovering new music. It never suggests genres the user hasn't listened to.
- Any decision that matters, like which artists get promoted or paid.

---

## 3. How the Model Works  

The recommender gives every song points for how well it fits the user, then shows the songs with the most points.

**What it looks at in each song:** genre, mood, energy (how calm or intense it is) and acousticness (acoustic vs. electronic sound). Tempo and danceability are left out because in this data they mostly rise and fall with energy, so they would count the same thing twice.

**What it knows about the user:** how much of their listening history each genre and mood makes up (for example, 50% pop, 30% lofi, 20% rock), how energetic they want songs to be, and whether they like acoustic music.

**How a song earns points:**

- **Genre, up to 2 points.** The user's most-listened genre gets the full 2 points. Other genres get points in proportion: if pop is 50% and lofi is 30%, a lofi song gets 2 × 30/50 = 1.2. A genre they never listen to gets nothing.
- **Mood, up to 1 point,** worked out the same way. Genre counts more than mood because people usually care more about the kind of music than the exact vibe.
- **Energy, up to 1 point.** The closer the song's energy is to what the user wants, the more points. Being close matters, not being higher or lower.
- **Acoustic, 0.5 points,** if the song's sound matches whether the user likes acoustic music.

**Choosing the songs:** every song in the catalog gets scored, the list is sorted from most to fewest points, and the top 5 are shown. Each recommendation lists the reasons it earned its points, such as "genre pop (+2.00)".

**Changes from the starter logic:** the starter profile had one favorite genre and one favorite mood. This version uses the user's listening-history percentages, so their second and third favorites still get partial credit.

---

## 4. Data  

**Size:** 20 songs in `data/songs.csv`. The starter file had 10; I added 10 more.

**Features per song:** title, artist, genre, mood, energy, tempo (BPM), valence (how happy it sounds), danceability and acousticness. The numbers are 0 to 1, except tempo.

**Genres (17):** pop, indie pop, lofi, rock, metal, ambient, jazz, synthwave, hip hop, classical, country, edm, r&b, folk, reggae, blues, latin.

**Moods (16):** happy, chill, intense, relaxed, moody, focused, confident, melancholic, nostalgic, euphoric, romantic, angry, playful, carefree, sad, energetic.

**What I added and why:** the 10 new songs all have new genres and moods. They also widen the range of valence (now 0.15 to 0.90) and tempo (66 to 176 BPM). Two of them break the starter pattern where high energy always meant low acousticness: an upbeat acoustic folk song and a calm electronic r&b song.

**Limits:**

- Most genres and moods have only 1 song. Lofi has 3, so lofi fans get the most real choices.
- In this data, energy, tempo, danceability and acousticness mostly move together, so they tell you nearly the same thing.
- The songs and artists are made up, and the numbers are estimates, not measured from real audio.
- There's nothing about lyrics, language, era, culture or popularity.

---

## 5. Strengths  

- **Clear, typical tastes work well.** Chill Lofi, High-Energy Pop and Deep Intense Rock all got a sensible #1 and a sensible top 3.
- **Opposite users get opposite lists.** The pop and lofi profiles share no songs.
- **Second-favorite genres count.** Because of the listening-history percentages, a lofi fan who also likes jazz and ambient gets those genres next, instead of random songs.
- **Every pick is explained.** Each recommendation lists exactly where its points came from, so it's easy to spot when something is wrong.
- **Closeness works for energy.** Users get songs near their energy level, not just the loudest or quietest ones.

---

## 6. Limitations and Bias 

**Weakness found: high-energy songs fill the gaps for everyone.** When a song doesn't match the user's genre or mood, the only thing left to score it on is energy (plus the small acoustic bonus). Half the catalog is loud, high-energy and electronic, so those same few songs fill the bottom of very different users' lists: *Gym Hero* appeared in the top 5 for 6 of the 8 profiles tested, including a metal fan and a sad blues fan. The system never asks whether a song "feels" right. A pop workout track gets recommended to someone who wants sad music just because the numbers are close. It also never suggests genres or moods the user hasn't listened to, so it keeps them in a filter bubble.

**Other limitations:**

- Genre and mood must match exactly. "Relaxed" and "chill" count as different moods, and "indie pop" gets no credit from a pop fan.
- The catalog is tiny (20 songs) and uneven. Lofi has 3 songs, while most genres and moods have only 1, so a blues or "sad" listener has just one real match.
- Valence (happy vs. sad sound), tempo, lyrics and language aren't considered at all.
- Scoring genre relative to the top choice means someone who likes four genres equally gets full genre points for all four, so their genre preference stops narrowing anything down.

---

## 7. Evaluation  

### Profiles tested

I ran 8 profiles through `python -m src.main` and checked whether the top 5 matched what that listener would actually want.

| Profile | What it tests |
|---|---|
| Default Pop/Happy | The starter profile, with some lofi and chill listening mixed in |
| High-Energy Pop | A typical upbeat pop fan |
| Chill Lofi | A typical calm study-music fan |
| Deep Intense Rock | A typical rock and metal fan |
| Sad but Hyped | **Edge case:** wants energy 0.9 *and* a sad mood, but the only sad song is calm |
| Ghost Genre (k-pop) | **Edge case:** favorite genre isn't in the catalog |
| Acoustic Headbanger | **Edge case:** loves metal *and* acoustic sound, but no song is both |
| Fence Sitter | **Edge case:** likes four genres equally, medium energy |

### Do the results feel right?

The three typical profiles feel right at the top. Chill Lofi gets three lofi songs, then ambient and jazz, all calm and acoustic. Rock gets *Storm Runner*, then the metal song. Pop gets *Sunrise City*. Things get worse further down each list, where songs are picked only for having similar energy.

### Why does *Sunrise City* rank first for High-Energy Pop?

It earns points on all four rules: pop genre (+2.00), happy mood (+1.00), energy 0.82 vs. a target of 0.9 (+0.92), and a non-acoustic sound (+0.50), for 4.42 in total. No other song matches both genre and mood, so nothing else can catch up. The best any other song can do is 3.5.

### Why does *Gym Hero* keep showing up? (plain language)

Think of the recommender as a judge handing out points. *Gym Hero* is labeled pop, which is worth the most points of anything, and it's one of the loudest, most energetic songs in the catalog. So for a "Happy Pop" fan, it gets the big pop points even though it's a workout song, not a happy one. For anyone who wants energetic music, it scores well on energy even when the genre is wrong. The judge only checks labels and numbers. It can't tell that a gym track isn't what a happy-pop listener or a sad-music listener had in mind.

### Comparing profiles

- **High-Energy Pop vs. Chill Lofi:** the two lists have no songs in common. Pop gets loud, non-acoustic songs (energy 0.76–0.93); lofi gets quiet acoustic ones (energy 0.28–0.42). This makes sense because every rule pulls in opposite directions for these two users.
- **Chill Lofi vs. Deep Intense Rock:** also no overlap. Lofi fills its list with similar genres it listens to (ambient, jazz). Rock's list runs out of rock and metal after two songs and fills the rest with any high-energy song (pop, edm, latin). Lofi has more matching songs in the catalog, so its list holds together better.
- **High-Energy Pop vs. Deep Intense Rock:** they share *Storm Runner*, *Gym Hero* and *Neon Fiesta* because both want very high energy and no acoustic sound. Gym Hero is 2nd for pop (genre match) and 3rd for rock (because its mood is "intense"). Same song, different reasons, which shows the reason strings are useful.
- **Default Pop/Happy vs. High-Energy Pop:** both are pop/happy, but the Default profile also lists 30% lofi and 40% chill, so two lofi songs move into 3rd and 4th place. High-Energy Pop has no lofi in its history, so its list stays upbeat. The listening-history percentages are clearly working.
- **High-Energy Pop vs. Ghost Genre (k-pop):** the k-pop fan gets no genre points for any song, so mood and energy decide. They still end up with the two happy pop songs at the top, which is a reasonable guess. But it only works because "happy" matched; the system has no idea k-pop is close to pop.
- **Deep Intense Rock vs. Acoustic Headbanger:** both put the metal song *Iron Verdict* at or near the top. But "likes acoustic" pulls a folk song and a **country** song into the headbanger's 2nd and 3rd places. That's the biggest surprise: a 0.5-point acoustic bonus beats loud songs that would actually suit a metal fan.
- **High-Energy Pop vs. Sad but Hyped:** the blues fan's only sad song, *Empty Station Blues*, is 1st even though its energy (0.33) is far from what they want (0.9), because genre + mood (3 points) beats energy (at most 1). Below it, the list is the same generic high-energy songs the pop fan gets. The system settles the conflict by trusting the labels and ignoring the energy.
- **Default Pop/Happy vs. Fence Sitter:** the Fence Sitter gets one song from each of their four genres. That's good variety, but each genre gets the full 2 points, so energy alone decides the order. Their 50% "sad" mood never shows up because the only sad song is blues, which isn't one of their genres.

### What surprised me

- *Gym Hero* in 6 of the 8 top-5 lists.
- A country song recommended to a metal fan because of the acoustic bonus.
- A sad, calm song winning for someone who asked for energy 0.9.

### Experiment: double energy, halve genre

I changed the genre weight from 2.0 to 1.0 and the energy weight from 1.0 to 2.0. The maximum possible score stays at 4.5, so the math is still valid and comparable. I tested this by overriding the weights in a separate run; the weights in `recommender.py` are unchanged.

| Profile | Before (top 5) | After (top 5) |
|---|---|---|
| Default Pop/Happy | Sunrise City, Gym Hero, Midnight Coding, Library Rain, Rooftop Lights | Sunrise City, **Rooftop Lights**, Gym Hero, Midnight Coding, Library Rain |
| Deep Intense Rock | Storm Runner, Iron Verdict, Gym Hero, Bassline Riot, Neon Fiesta | same order; Gym Hero's score rose from 2.48 to 3.46 |
| Acoustic Headbanger | Iron Verdict, Harvest Fiddle Run, Dusty Porch Swing, Bassline Riot, Gym Hero | Iron Verdict, Harvest Fiddle Run, Bassline Riot, Gym Hero, **Storm Runner** |
| Fence Sitter | Sunrise City, Dusty Porch Swing, Coffee Shop Stories, Storm Runner, Gym Hero | ..., **Empty Station Blues**, **Rooftop Lights** replace Storm Runner and Gym Hero |
| Other 4 profiles | | same order, different scores |

**More accurate or just different? Mostly just different.** Some changes are better: *Rooftop Lights* (happy, right energy) moves up for the pop fan, and the country song drops off the metal fan's list in favor of *Storm Runner*. But the #1 song didn't change for any profile, and high-energy filler like *Gym Hero* got *stronger* for the rock fan. Lowering genre makes the system lean even more on energy, which is the weakness described in Limitations. I kept the original weights.

### Automated tests

`pytest` passes both starter tests in `tests/test_recommender.py`: songs come back sorted by score with the pop/happy song first, and the explanation is a non-empty string.

### Test outputs (original weights)

**Default Pop/Happy**

```
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

**High-Energy Pop**

```
============================================================
  Top Recommendations: High-Energy Pop
============================================================
  Genres: pop
  Moods:  happy
  Target energy: 0.9
  Likes acoustic: no
------------------------------------------------------------

1. Sunrise City by Neon Echo
   pop / happy   Score: 4.42
     - genre pop (+2.00)
     - mood happy (+1.00)
     - energy 0.82 close to target (+0.92)
     - non-acoustic sound (+0.50)

2. Gym Hero by Max Pulse
   pop / intense   Score: 3.47
     - genre pop (+2.00)
     - energy 0.93 close to target (+0.97)
     - non-acoustic sound (+0.50)

3. Rooftop Lights by Indigo Parade
   indie pop / happy   Score: 2.36
     - mood happy (+1.00)
     - energy 0.76 close to target (+0.86)
     - non-acoustic sound (+0.50)

4. Storm Runner by Voltline
   rock / intense   Score: 1.49
     - energy 0.91 close to target (+0.99)
     - non-acoustic sound (+0.50)

5. Neon Fiesta by Sol Rumbero
   latin / energetic   Score: 1.47
     - energy 0.87 close to target (+0.97)
     - non-acoustic sound (+0.50)
```

**Chill Lofi**

```
============================================================
  Top Recommendations: Chill Lofi
============================================================
  Genres: lofi 60%, jazz 25%, ambient 15%
  Moods:  chill 70%, focused 30%
  Target energy: 0.35
  Likes acoustic: yes
------------------------------------------------------------

1. Library Rain by Paper Lanterns
   lofi / chill   Score: 4.50
     - genre lofi (+2.00)
     - mood chill (+1.00)
     - energy 0.35 close to target (+1.00)
     - acoustic sound (+0.50)

2. Midnight Coding by LoRoom
   lofi / chill   Score: 4.43
     - genre lofi (+2.00)
     - mood chill (+1.00)
     - energy 0.42 close to target (+0.93)
     - acoustic sound (+0.50)

3. Focus Flow by LoRoom
   lofi / focused   Score: 3.88
     - genre lofi (+2.00)
     - mood focused (+0.43)
     - energy 0.40 close to target (+0.95)
     - acoustic sound (+0.50)

4. Spacewalk Thoughts by Orbit Bloom
   ambient / chill   Score: 2.93
     - genre ambient (+0.50)
     - mood chill (+1.00)
     - energy 0.28 close to target (+0.93)
     - acoustic sound (+0.50)

5. Coffee Shop Stories by Slow Stereo
   jazz / relaxed   Score: 2.31
     - genre jazz (+0.83)
     - energy 0.37 close to target (+0.98)
     - acoustic sound (+0.50)
```

**Deep Intense Rock**

```
============================================================
  Top Recommendations: Deep Intense Rock
============================================================
  Genres: rock 60%, metal 40%
  Moods:  intense 60%, angry 40%
  Target energy: 0.95
  Likes acoustic: no
------------------------------------------------------------

1. Storm Runner by Voltline
   rock / intense   Score: 4.46
     - genre rock (+2.00)
     - mood intense (+1.00)
     - energy 0.91 close to target (+0.96)
     - non-acoustic sound (+0.50)

2. Iron Verdict by Graveforge
   metal / angry   Score: 3.47
     - genre metal (+1.33)
     - mood angry (+0.67)
     - energy 0.98 close to target (+0.97)
     - non-acoustic sound (+0.50)

3. Gym Hero by Max Pulse
   pop / intense   Score: 2.48
     - mood intense (+1.00)
     - energy 0.93 close to target (+0.98)
     - non-acoustic sound (+0.50)

4. Bassline Riot by Kilowatt Kids
   edm / euphoric   Score: 1.49
     - energy 0.96 close to target (+0.99)
     - non-acoustic sound (+0.50)

5. Neon Fiesta by Sol Rumbero
   latin / energetic   Score: 1.42
     - energy 0.87 close to target (+0.92)
     - non-acoustic sound (+0.50)
```

**Sad but Hyped**

```
============================================================
  Top Recommendations: Sad but Hyped
============================================================
  Genres: blues
  Moods:  sad
  Target energy: 0.9
  Likes acoustic: no
------------------------------------------------------------

1. Empty Station Blues by Hollis Gray
   blues / sad   Score: 3.43
     - genre blues (+2.00)
     - mood sad (+1.00)
     - energy 0.33 close to target (+0.43)

2. Storm Runner by Voltline
   rock / intense   Score: 1.49
     - energy 0.91 close to target (+0.99)
     - non-acoustic sound (+0.50)

3. Gym Hero by Max Pulse
   pop / intense   Score: 1.47
     - energy 0.93 close to target (+0.97)
     - non-acoustic sound (+0.50)

4. Neon Fiesta by Sol Rumbero
   latin / energetic   Score: 1.47
     - energy 0.87 close to target (+0.97)
     - non-acoustic sound (+0.50)

5. Bassline Riot by Kilowatt Kids
   edm / euphoric   Score: 1.44
     - energy 0.96 close to target (+0.94)
     - non-acoustic sound (+0.50)
```

**Ghost Genre (k-pop)**

```
============================================================
  Top Recommendations: Ghost Genre (k-pop)
============================================================
  Genres: k-pop
  Moods:  happy
  Target energy: 0.7
  Likes acoustic: no
------------------------------------------------------------

1. Rooftop Lights by Indigo Parade
   indie pop / happy   Score: 2.44
     - mood happy (+1.00)
     - energy 0.76 close to target (+0.94)
     - non-acoustic sound (+0.50)

2. Sunrise City by Neon Echo
   pop / happy   Score: 2.38
     - mood happy (+1.00)
     - energy 0.82 close to target (+0.88)
     - non-acoustic sound (+0.50)

3. Night Drive Loop by Neon Echo
   synthwave / moody   Score: 1.45
     - energy 0.75 close to target (+0.95)
     - non-acoustic sound (+0.50)

4. Concrete Crown by Block Theory
   hip hop / confident   Score: 1.42
     - energy 0.78 close to target (+0.92)
     - non-acoustic sound (+0.50)

5. Neon Fiesta by Sol Rumbero
   latin / energetic   Score: 1.33
     - energy 0.87 close to target (+0.83)
     - non-acoustic sound (+0.50)
```

**Acoustic Headbanger**

```
============================================================
  Top Recommendations: Acoustic Headbanger
============================================================
  Genres: metal
  Moods:  angry
  Target energy: 0.95
  Likes acoustic: yes
------------------------------------------------------------

1. Iron Verdict by Graveforge
   metal / angry   Score: 3.97
     - genre metal (+2.00)
     - mood angry (+1.00)
     - energy 0.98 close to target (+0.97)

2. Harvest Fiddle Run by The Copper Pines
   folk / playful   Score: 1.36
     - energy 0.81 close to target (+0.86)
     - acoustic sound (+0.50)

3. Dusty Porch Swing by Willow Creek Band
   country / nostalgic   Score: 1.13
     - energy 0.58 close to target (+0.63)
     - acoustic sound (+0.50)

4. Bassline Riot by Kilowatt Kids
   edm / euphoric   Score: 0.99
     - energy 0.96 close to target (+0.99)

5. Gym Hero by Max Pulse
   pop / intense   Score: 0.98
     - energy 0.93 close to target (+0.98)
```

**Fence Sitter**

```
============================================================
  Top Recommendations: Fence Sitter
============================================================
  Genres: pop 25%, rock 25%, jazz 25%, country 25%
  Moods:  happy 50%, sad 50%
  Target energy: 0.5
------------------------------------------------------------

1. Sunrise City by Neon Echo
   pop / happy   Score: 3.68
     - genre pop (+2.00)
     - mood happy (+1.00)
     - energy 0.82 close to target (+0.68)

2. Dusty Porch Swing by Willow Creek Band
   country / nostalgic   Score: 2.92
     - genre country (+2.00)
     - energy 0.58 close to target (+0.92)

3. Coffee Shop Stories by Slow Stereo
   jazz / relaxed   Score: 2.87
     - genre jazz (+2.00)
     - energy 0.37 close to target (+0.87)

4. Storm Runner by Voltline
   rock / intense   Score: 2.59
     - genre rock (+2.00)
     - energy 0.91 close to target (+0.59)

5. Gym Hero by Max Pulse
   pop / intense   Score: 2.57
     - genre pop (+2.00)
     - energy 0.93 close to target (+0.57)
```

---

## 8. Future Work  

1. **Group similar moods and genres.** Treat "chill", "relaxed" and "peaceful" as close matches that get partial points, and do the same for "pop" and "indie pop". This fixes the exact-label problem.
2. **Add valence to the profile.** A target "happy vs. sad" level would keep sad songs away from happy listeners and help break ties among the high-energy filler songs.
3. **Make the top 5 more varied.** Limit each list to one song per artist, and save one slot for a song from a genre the user hasn't heard, to soften the filter bubble.

---

## 9. Personal Reflection  

**Biggest learning moment:** realizing that a recommendation is just math. Every "pick" comes from a few weights and a closeness formula, and even small changes to them have a big impact. Changing two weights in my experiment reshuffled several users' top 5 lists.

**How AI tools helped, and when I double-checked:** I mainly used AI for code generation and automated tests. I did the logical reasoning myself and double-checked the results: I ran each profile, looked at whether the rankings made sense, and questioned the ones that didn't, like a country song showing up for a metal fan.

**What surprised me:** how accurate it feels. Something as complex as human taste and emotion can be boiled down to a few numbers, like genre share, mood and energy, and still produce a list that feels like it was picked for you.

**What I'd try next:** artist recommendations using a graph model. It would connect songs, albums and artists through the listeners they share, and recommend based on those links. That would also help with discovery, since it could suggest artists outside the genres a user already listens to.
