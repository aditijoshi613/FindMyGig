"""Streamlit UI for the live music recommendation agent."""
import html
import re
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage

from src.graph import build_agent

# Keys we expect from the LLM for each event (order preserved for display)
EVENT_KEYS = ["Title", "Venue", "Time", "Artists", "Description"]

GENRE_OPTIONS = [
    "Indie",
    "Acoustic",
    "Jazz",
    "Rock",
    "Electronic",
    "Folk",
    "Punk",
    "Soul & R&B",
    "Hip-hop",
    "Classical",
    "Metal",
    "Pop",
]

TIME_RANGE_OPTIONS = {
    "Next week": "in the next week",
    "Next 2 weeks": "in the next 2 weeks",
    "This month": "this month",
}


FORMAT_INSTRUCTION = """
For each event you recommend, format it exactly like this (one block per event, separate blocks with ---):
Title: [event name]
Venue: [venue name and location]
Time: [date and time]
Artists: [artist(s) or band names]
Description: [short description or why you recommend it]
---
"""


def build_prompt(location: str, genres: list[str], time_label: str) -> str:
    time_phrase = TIME_RANGE_OPTIONS.get(time_label, "in the next 2 weeks")
    if not genres:
        base = f"I'm in {location}. What gigs do you recommend {time_phrase}?"
    else:
        vibe = ", ".join(genres)
        base = (
            f"I'm in {location} and love {vibe} vibes. "
            f"What gigs do you recommend {time_phrase}?"
        )
    return base + "\n\n" + FORMAT_INSTRUCTION


def parse_events(text: str) -> list[dict[str, str]]:
    """Parse LLM response into list of event dicts (Title, Venue, Time, Artists, Description)."""
    events = []
    blocks = re.split(r"\s*---\s*", text.strip())
    key_pattern = re.compile(r"^(" + "|".join(re.escape(k) for k in EVENT_KEYS) + r"):\s*(.*)$", re.MULTILINE | re.IGNORECASE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        event: dict[str, str] = {k: "" for k in EVENT_KEYS}
        for m in key_pattern.finditer(block):
            key, value = m.group(1), m.group(2).strip()
            for k in EVENT_KEYS:
                if k.lower() == key.lower():
                    event[k] = value
                    break
        if event.get("Title") or any(event.values()):
            events.append(event)
    return events


# ---- Page config ----
st.set_page_config(
    page_title="Find My Gig",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- Custom CSS ----
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
    .stApp { background: linear-gradient(165deg, #0f0f12 0%, #1a1a22 40%, #12121a 100%); }
    .stApp [data-testid="stVerticalBlock"] > div { max-width: 720px; margin-left: auto; margin-right: auto; }
    .hero { text-align: center; padding: 2rem 0 2.5rem; }
    .hero h1 { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 2.75rem; letter-spacing: -0.02em;
               color: #fff; margin: 0; }
    .hero p { font-family: 'Outfit', sans-serif; font-size: 1.1rem; color: #94a3b8; margin: 0.5rem 0 0; }
    .section-label { font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 0.85rem; color: #94a3b8;
                     text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.75rem; }
    .result-card { font-family: 'Outfit', sans-serif; background: rgba(30,30,38,0.9); border: 1px solid #2e2e3a;
                   border-radius: 12px; padding: 1.5rem 1.75rem; margin-top: 1rem; color: #e2e8f0; line-height: 1.6; }
    .result-card h3 { color: #f59e0b; font-size: 0.9rem; margin: 0 0 0.75rem; }
    .event-card { font-family: 'Outfit', sans-serif; background: rgba(30,30,38,0.95); border: 1px solid #2e2e3a;
                  border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; color: #e2e8f0; }
    .event-card:last-child { margin-bottom: 0; }
    .event-card-title { font-weight: 700; font-size: 1.1rem; color: #fff; margin: 0 0 1rem; }
    .event-card-field { margin-bottom: 0.6rem; font-size: 0.9rem; line-height: 1.5; }
    .event-card-field strong { color: #94a3b8; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }
    .event-card-field strong::after { content: ' '; }
    .stButton > button { font-family: 'Outfit', sans-serif !important; font-weight: 600 !important;
                         border-radius: 10px !important; transition: transform 0.15s ease, box-shadow 0.15s ease !important; }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(245,158,11,0.25); }
    [data-testid="stMetricValue"] { font-family: 'Outfit', sans-serif !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Hero ----
st.markdown(
    '<div class="hero"><h1>🎵 Find My Gig</h1><p>Your vibe, your city, your gig.</p></div>',
    unsafe_allow_html=True,
)

# ---- Centered form ----
if "genres" not in st.session_state:
    st.session_state["genres"] = set()
if "time_range" not in st.session_state:
    st.session_state["time_range"] = "Next 2 weeks"


def toggle_genre(genre: str) -> None:
    s = st.session_state.get("genres", set())
    if genre in s:
        s.discard(genre)
    else:
        s.add(genre)
    st.session_state["genres"] = s


def set_time_range(label: str) -> None:
    st.session_state["time_range"] = label


# Location
st.markdown('<p class="section-label">Where</p>', unsafe_allow_html=True)
location = st.text_input(
    "Location",
    placeholder="e.g. Brooklyn, London, San Francisco",
    key="location",
    label_visibility="collapsed",
)

# Genre chips (multi-select buttons)
st.markdown('<p class="section-label">Genre / vibe</p>', unsafe_allow_html=True)
genre_cols = st.columns(4)
for i, genre in enumerate(GENRE_OPTIONS):
    with genre_cols[i % 4]:
        is_selected = genre in st.session_state["genres"]
        st.button(
            genre,
            type="primary" if is_selected else "secondary",
            use_container_width=True,
            key=f"genre_{genre}",
            on_click=toggle_genre,
            args=(genre,),
        )
selected_genres = sorted(st.session_state["genres"])

# Time range
st.markdown('<p class="section-label">When</p>', unsafe_allow_html=True)
time_cols = st.columns(3)
for col, label in zip(time_cols, TIME_RANGE_OPTIONS):
    with col:
        is_selected = st.session_state["time_range"] == label
        st.button(
            label,
            type="primary" if is_selected else "secondary",
            use_container_width=True,
            key=f"time_{label}",
            on_click=set_time_range,
            args=(label,),
        )
time_range = st.session_state["time_range"]

st.markdown("<br>", unsafe_allow_html=True)

# Main CTA
recommend = st.button(
    "Get recommendations",
    type="primary",
    use_container_width=True,
)

if recommend:
    if not location or not location.strip():
        st.warning("Please enter a location.")
    else:
        prompt = build_prompt(location.strip(), selected_genres, time_range)
        with st.spinner("Finding gigs for you…"):
            try:
                agent = build_agent()
                full_content = []
                for chunk in agent.stream({"messages": [HumanMessage(content=prompt)]}):
                    if "agent" in chunk:
                        for m in chunk["agent"]["messages"]:
                            if hasattr(m, "content") and m.content:
                                full_content.append(m.content)
                if full_content:
                    text = "\n\n".join(full_content)
                    events = parse_events(text)
                    if events:
                        st.markdown('<p class="section-label">Recommendations</p>', unsafe_allow_html=True)
                        for ev in events:
                            title = html.escape(ev.get("Title", "Event") or "Event")
                            parts = []
                            for key in ["Venue", "Time", "Artists", "Description"]:
                                val = (ev.get(key) or "").strip()
                                if val:
                                    val_esc = html.escape(val).replace("\n", "<br>")
                                    parts.append(f'<div class="event-card-field"><strong>{key}</strong>{val_esc}</div>')
                            inner = "\n".join(parts)
                            st.markdown(
                                f'<div class="event-card"><div class="event-card-title">{title}</div>{inner}</div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        text_escaped = html.escape(text).replace("\n", "<br>")
                        st.markdown(
                            f'<div class="result-card"><h3>Recommendations</h3><div>{text_escaped}</div></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No recommendations this time. Try a different location or vibe.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
