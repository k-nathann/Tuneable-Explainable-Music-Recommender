"""
Streamlit UI for Tuneable — the explainable music recommender.

Run locally from the project root with:

    streamlit run streamlit_app.py

It is a thin presentation layer over src/recommender.py: it collects a taste
profile from the sidebar, calls the exact same scoring engine the CLI uses, and
renders the ranked, explained recommendations.
"""

from typing import Dict, List

import pandas as pd
import streamlit as st

from src.recommender import STRATEGIES, load_songs, recommend_songs

DATA_PATH = "data/songs.csv"


@st.cache_data
def get_songs() -> List[Dict]:
    """Load and cache the catalog so we don't re-read the CSV on every rerun."""
    return load_songs(DATA_PATH)


def sorted_unique(songs: List[Dict], key: str) -> List[str]:
    """Distinct, sorted values for a categorical column (for dropdowns)."""
    return sorted({str(song[key]) for song in songs})


st.set_page_config(page_title="Tuneable — Music Recommender", page_icon="🎵")

songs = get_songs()

st.title("🎵 Tuneable")
st.caption(
    "An explainable, content-based music recommender. Set a taste profile and "
    "see the top picks — each with a plain-language reason for *why* it scored."
)

# --- Sidebar: the taste profile -------------------------------------------------
with st.sidebar:
    st.header("Your taste profile")

    genres = sorted_unique(songs, "genre")
    moods = sorted_unique(songs, "mood")

    favorite_genre = st.selectbox(
        "Favorite genre", genres, index=genres.index("pop") if "pop" in genres else 0
    )
    favorite_mood = st.selectbox(
        "Favorite mood", moods, index=moods.index("happy") if "happy" in moods else 0
    )
    target_energy = st.slider("Target energy", 0.0, 1.0, 0.80, 0.01)

    st.divider()
    st.subheader("Ranking options")

    strategy_name = st.selectbox("Scoring strategy", list(STRATEGIES.keys()))
    diversify = st.toggle(
        "Diversify results",
        value=False,
        help="Penalize repeated artists/genres so the list spreads across the catalog.",
    )
    top_k = st.slider("How many recommendations", 1, min(10, len(songs)), 5)

    st.divider()
    with st.expander("Advanced feature targets (optional)"):
        st.caption(
            "These refine ties — they never overrule genre, mood, or energy."
        )
        use_advanced = st.checkbox("Enable advanced targets")
        target_popularity = st.slider("Target popularity", 0, 100, 65)
        preferred_decade = st.selectbox(
            "Preferred decade", sorted_unique(songs, "release_decade")
        )
        target_instrumentalness = st.slider(
            "Target instrumentalness", 0.0, 1.0, 0.5, 0.01
        )

# --- Build the prefs dict the engine expects ------------------------------------
prefs: Dict = {
    "favorite_genre": favorite_genre,
    "favorite_mood": favorite_mood,
    "target_energy": target_energy,
}
if use_advanced:
    prefs["target_popularity"] = target_popularity
    prefs["preferred_decade"] = int(preferred_decade)
    prefs["target_instrumentalness"] = target_instrumentalness

strategy = STRATEGIES[strategy_name]
recommendations = recommend_songs(
    prefs, songs, k=top_k, strategy=strategy, diversify=diversify
)

# --- Summary line ---------------------------------------------------------------
mode_bits = [f"**{strategy_name}** strategy"]
if diversify:
    mode_bits.append("diversity **on**")
st.markdown(
    f"Top **{top_k}** for a *{favorite_genre} / {favorite_mood}* listener "
    f"(target energy **{target_energy:.2f}**) — {', '.join(mode_bits)}."
)

# --- Score chart ----------------------------------------------------------------
chart_df = pd.DataFrame(
    {"song": [song["title"] for song, _, _ in recommendations],
     "score": [score for _, score, _ in recommendations]}
).set_index("song")
st.bar_chart(chart_df, horizontal=True)

# --- Ranked cards with explanations ---------------------------------------------
for rank, (song, score, explanation) in enumerate(recommendations, start=1):
    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.markdown(f"### {rank}. {song['title']}")
            st.markdown(
                f"**{song['artist']}** · {song['genre']} / {song['mood']} · "
                f"energy {song['energy']:.2f}"
            )
        with right:
            st.metric("Score", f"{score:.2f}")
        st.markdown("**Why this pick:**")
        for reason in explanation.split("; "):
            st.markdown(f"- {reason}")

# --- Full catalog for reference -------------------------------------------------
with st.expander(f"Browse the full {len(songs)}-track catalog"):
    st.dataframe(pd.DataFrame(songs), use_container_width=True, hide_index=True)

st.caption(
    "Built on the same scoring engine as the CLI (`src/recommender.py`). "
    "See the [model card](model_card.md) for limitations and bias analysis."
)
