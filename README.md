# 🎵 Tuneable — Explainable Music Recommender

A small, **content-based music recommender** that scores a catalog of songs
against a listener's stated taste profile and returns ranked recommendations —
each one accompanied by a plain-language reason for *why* it was picked.

Built as a teaching artifact for understanding how a scoring "judge" turns raw
preferences into ranked, explainable results.

---

## ✨ Features

- **Transparent scoring** — every recommendation shows its exact point
  breakdown (e.g. `genre match: pop (+2.0); energy fit: 0.95 (+0.95)`), so
  there's no black box.
- **Two APIs, one scorer** — a dict-based functional path (`score_song`,
  `recommend_songs`) and an OOP path (`Song`, `UserProfile`, `Recommender`)
  that both delegate to a single shared scoring function.
- **Swappable strategies** *(Strategy pattern)* — `Balanced`, `Genre-First`,
  `Mood-First`, and `Energy-Focused` weight sets change which signal dominates
  without touching the formula.
- **Diversity re-ranking** — an optional greedy penalty stops a single artist
  or genre from dominating the results.
- **Advanced feature scoring** — optional popularity, release-decade, and
  instrumentalness terms that refine ties without overruling the core signals.
- **Clean ASCII table output** — a pure-standard-library, word-wrapped table
  renderer (no external table dependency).
- **Model card included** — a formal [model card](model_card.md) documenting
  intended use, limitations, and bias risks.

---

## 🧠 How It Works

Each `Song` carries features such as genre, mood, energy, tempo, valence,
danceability, and acousticness. A `UserProfile` (or a plain prefs dict) states a
`favorite_genre`, `favorite_mood`, and `target_energy`.

The scorer awards points on a **max scale of 4.0**:

| Signal  | Rule                                                    | Points |
| ------- | ------------------------------------------------------- | ------ |
| Genre   | exact match, all-or-nothing                             | +2.0   |
| Mood    | exact match, all-or-nothing                             | +1.0   |
| Energy  | closeness to target: `1 − |target − value|` (clamped ≥0) | up to +1.0 |

Categorical signals (genre, mood) are all-or-nothing; the numeric energy term
earns **partial credit** based on how close it is to the target and never goes
negative. Songs are then sorted highest-first, and the top *k* are returned.

Optional strategies simply feed a different weight set into the same scorer, and
the diversity option multiplies a candidate's score by `0.5` for each
already-picked song that shares its artist or genre.

---

## 🚀 Getting Started

### Setup

```bash
# 1. (optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 2. install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
python -m src.main
```

This stress-tests the recommender against several user profiles — including
adversarial and edge-case profiles with conflicting preferences — and prints the
top 5 songs for each as a formatted table, plus strategy and diversity demos.

### Run the tests

```bash
pytest
```

---

## 📊 Sample Output

Running with the default balanced profile (`favorite_genre=pop`,
`favorite_mood=happy`, `target_energy=0.80`) produces ranked results with a
transparent reason for each pick:

```
===================================================
Top 5 for profile: pop / happy (target energy 0.80)
===================================================

1. Sunrise City — Neon Echo
   Genre/Mood: pop / happy
   Score: 3.98 / 4.0
   Reasons:
     • genre match: pop (+2.0)
     • mood match: happy (+1.0)
     • energy fit: 0.98 (target 0.80 vs 0.82) (+0.98)

2. Gym Hero — Max Pulse
   Genre/Mood: pop / intense
   Score: 2.87 / 4.0
   Reasons:
     • genre match: pop (+2.0)
     • energy fit: 0.87 (target 0.80 vs 0.93) (+0.87)
```

**Why this makes sense:** *Sunrise City* matches all three criteria (pop **and**
happy **and** ~0.8 energy), so it tops the list. *Gym Hero* is pop but
"intense," so it keeps the genre points but loses the mood bonus.

---

## 📁 Project Structure

```
.
├── src/
│   ├── main.py           # CLI runner: profiles, strategy/diversity demos, table output
│   └── recommender.py    # Song/UserProfile/Recommender, scoring engine, strategies
├── tests/
│   └── test_recommender.py
├── data/
│   └── songs.csv         # 18-track catalog
├── model_card.md         # intended use, limitations, bias analysis
├── ai_interactions.md    # notes on AI-assisted development
├── requirements.txt
└── README.md
```

---

## ⚠️ Limitations

- Operates on a tiny **18-track catalog** — not representative of a real
  library.
- Understands only structured features, **not lyrics or audio** itself.
- Assumes a user's stated preferences are internally consistent; behavior on
  contradictory tastes (e.g. "sad but high-energy") is intentionally exercised
  in the stress tests.
- Can over-favor a single genre or mood without the diversity option enabled.

See the [model card](model_card.md) for a fuller discussion of limitations and
where bias could surface.

---

## 🛠️ Tech Stack

Python · pandas · pytest · Streamlit


