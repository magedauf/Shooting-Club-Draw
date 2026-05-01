import streamlit as st
import random
import json
import os
import time
from datetime import datetime
import pytz

# --- Persistence ---
STATE_FILE = "raffle_state.json"
NAMES_FILE = "names.txt"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                pass
    return {"winners": [], "bg_opacity": 0.12, "is_drawing": False, "participants": [], "last_init": "", "reset_count": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_names():
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def get_local_time():
    try:
        cairo_tz = pytz.timezone('Africa/Cairo')
        local_now = datetime.now(cairo_tz)
    except:
        from datetime import timedelta
        local_now = datetime.utcnow() + timedelta(hours=3)
    return local_now.strftime("%A, %B %d | %H:%M")

state = load_state()
master_names = load_names()

# --- Custom Styling & Layout ---
st.set_page_config(page_title="Shooting Club", page_icon="🦆", layout="centered")

bg_url = "https://raw.githubusercontent.com/magedauf/Shooting-Club-Draw/main/bg.jpg"
bg_opacity = state.get("bg_opacity", 0.12)

st.markdown(f"""
    <style>
    .stApp {{
        background-color: #000000;
        background: linear-gradient(rgba(0, 0, 0, {1 - bg_opacity}), rgba(0, 0, 0, {1 - bg_opacity})), 
                    url("{bg_url}");
        background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff;
    }}
    
    .block-container {{
        padding-top: 3.5rem !important;
        padding-bottom: 0rem !important;
    }}

    .top-title {{
        text-align: center;
        width: 100%;
        font-size: 1.8rem !important;
        font-weight: bold;
        padding-top: 2rem; 
        padding-bottom: 0.5rem;
        text-shadow: 2px 2px 5px #000000;
        letter-spacing: 1px;
    }}

    [data-testid="stSidebar"] {{ background-color: #2c2c2c; color: #ffffff; }}
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{ color: #ffffff !important; }}

    .welcome-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 30vh;
        text-align: center;
    }}
    
    .welcome-main-text {{ font-size: 1.9rem !important; font-weight: bold; margin-bottom: 0px !important; text-shadow: 2px 2px 4px #000000; }}
    .time-text {{ font-size: 0.95rem !important; opacity: 0.8; margin-top: 8px; }}
    
    .stExpander {{ background-color: rgba(255,255,255,0.05) !important; border: none !important; }}

    /* Flying Ducks Animation */
    @keyframes fly {{
        0% {{ transform: translateX(-100%) translateY(0px); opacity: 0; }}
        20% {{ opacity: 0.5; }}
        80% {{ opacity: 0.5; }}
        100% {{ transform: translateX(200%) translateY(-50px); opacity: 0; }}
    }}

    .duck-fly {{
        position: fixed;
        font-size: 40px;
        z-index: 999;
        pointer-events: none;
        animation: fly 4s linear infinite;
        opacity: 0.5;
    }}
    </style>
    """, unsafe_allow_html=True)

# Function to trigger flying ducks
def trigger_ducks():
    duck_html = ""
    for i in range(5):
        top_pos = random.randint(10, 80)
        delay = random.uniform(0, 2)
        duck_html += f'<div class="duck-fly" style="top: {top_pos}%; animation-delay: {delay}s;">🦆</div>'
    st.markdown(duck_html, unsafe_allow_html=True)

# --- Sidebar ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=100)

st.sidebar.title("🎯 Control")
access = st.sidebar.selectbox("Access", ["Visitor", "Admin", "Super Admin"])
pwd = st.sidebar.text_input("Key", type="password")

is_super = (access == "Super Admin" and pwd == "maged_super_2026")
is_admin = (access == "Admin" and pwd == "team_admin_2026") or is_super

# Super Admin Controls (Restored Background Slider)
if is_super:
    st.sidebar.subheader("🎨 Visual Settings")
    new_opacity = st.sidebar.slider("Background Visibility", 0.0, 1.0, float(state.get("bg_opacity", 0.12)))
    if new_opacity != state["bg_opacity"]:
        state["bg_opacity"] = new_opacity
        save_state(state)
        st.rerun()

if is_admin:
    st.sidebar.divider()
    if st.sidebar.button("🔄 Initialize Draw"):
        state["winners"], state["participants"], state["is_drawing"] = [], [], False
        state["last_init"] = get_local_time()
        state["reset_count"] = state.get("reset_count", 0) + 1
        save_state(state)
        st.markdown('<script>window.parent.location.reload();</script>', unsafe_allow_html=True)
        st.rerun()

    if not state.get("winners") and not state.get("is_drawing"):
        st.sidebar.subheader("📝 Setup")
        current_key = f"contestants_{state.get('reset_count', 0)}"
        selected_names = st.sidebar.multiselect("Names", options=master_names, key=current_key)
        state["participants"] = selected_names
        save_state(state)
        
        num_winners = st.sidebar.selectbox("Winners", range(1, 11), index=0, key=f"win_{state.get('reset_count', 0)}")
        if st.sidebar.button("🔥 EXECUTE"):
            if selected_names:
                state["is_drawing"] = True
                save_state(state)
                state["winners"] = random.sample(selected_names, min(num_winners, len(selected_names)))
                state["is_drawing"] = False
                save_state(state)
                st.rerun()

# --- Main Interface ---
st.markdown('<div class="top-title">🦆 SHOOTING CLUB 🦆</div>', unsafe_allow_html=True)

main_zone = st.empty()

if state.get("is_drawing"):
    with main_zone.container():
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.header("🥁 SHUFFLING...")
        st.spinner("Selecting...")
        time.sleep(2)
        st.rerun()

elif state.get("winners"):
    with main_zone.container():
        st.header("🏆 Winners")
        # Trigger the 50% opacity flying ducks
        trigger_ducks()
        for i, winner in enumerate(state["winners"]):
            st.subheader(f"#{i+1}: {winner}")
            time.sleep(3.0) 
        
        with st.expander("Entry List"):
            st.write(", ".join(state["participants"]))
else:
    st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-main-text">Welcome To The DRAW</div>
            <p class="time-text">{state.get('last_init', '')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if state.get("participants") and len(state["participants"]) > 0:
        with st.expander("Round Contestants", expanded=True):
            st.write(", ".join(state["participants"]))

# Visitor Auto-Refresh
time.sleep(10)
st.rerun()
