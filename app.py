import streamlit as st
import random
import json
import os
import time
from datetime import datetime
import pytz # New library for accurate time

# --- Persistence ---
STATE_FILE = "raffle_state.json"
NAMES_FILE = "names.txt"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try:
                data = json.load(f)
                return data
            except:
                pass
    return {"winners": [], "bg_opacity": 0.5, "is_drawing": False, "participants": [], "last_init": ""}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_names():
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

# Helper function for exact Cairo Time (UTC+3)
def get_local_time():
    # This forces the app to use Cairo's timezone regardless of where the server is
    cairo_tz = pytz.timezone('Africa/Cairo')
    local_now = datetime.now(cairo_tz)
    return local_now.strftime("%A, %B %d, %Y | %H:%M:%S")

state = load_state()
master_names = load_names()

# --- Custom Styling & Branding ---
st.set_page_config(page_title="Shooting Club Draw", page_icon="🦆", layout="wide")

bg_url = "https://raw.githubusercontent.com/magedauf/Shooting-Club-Draw/main/bg.jpg"
bg_opacity = state.get("bg_opacity", 0.5)

st.markdown(f"""
    <style>
    .stApp {{
        background-color: #000000;
        background: linear-gradient(rgba(0, 0, 0, {1 - bg_opacity}), rgba(0, 0, 0, {1 - bg_opacity})), 
                    url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
    }}
    [data-testid="stSidebar"] {{ background-color: #2c2c2c; color: #ffffff; }}
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{ color: #ffffff !important; }}
    .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 50vh; text-align: center; }}
    h1, h2, h3 {{ color: #ffffff !important; text-shadow: 2px 2px 4px #000000; }}
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar & Authentication ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=150)

st.sidebar.title("🎯 Control Panel")
access = st.sidebar.selectbox("Access Level", ["Visitor", "Admin", "Super Admin"])
pwd = st.sidebar.text_input("Access Key", type="password")

is_super = (access == "Super Admin" and pwd == "maged_super_2026")
is_admin = (access == "Admin" and pwd == "team_admin_2026") or is_super

# --- Super Admin Controls ---
if is_super:
    st.sidebar.subheader("🎨 Visual Settings")
    new_opacity = st.sidebar.slider("Background Visibility", 0.0, 1.0, float(state.get("bg_opacity", 0.5)))
    if new_opacity != state["bg_opacity"]:
        state["bg_opacity"] = new_opacity
        save_state(state)
        st.rerun()

# --- Admin Controls ---
if is_admin:
    st.sidebar.divider()
    if st.sidebar.button("🔄 Initialize New Draw"):
        new_state = {
            "winners": [],
            "participants": [],
            "is_drawing": False,
            "last_init": get_local_time(), 
            "bg_opacity": state["bg_opacity"]
        }
        save_state(new_state)
        st.rerun()

    if not state.get("winners") and not state.get("is_drawing"):
        st.sidebar.subheader("📝 Round Setup")
        contestants = st.sidebar.multiselect("Select Contestants", options=master_names)
        
        if contestants:
            state["participants"] = contestants
            save_state(state)

        num_winners = st.sidebar.selectbox("Number of Winners", range(1, 11), index=0)
        
        if st.sidebar.button("🔥 EXECUTE DRAW"):
            if contestants:
                state["is_drawing"] = True
                save_state(state)
                picked = random.sample(contestants, min(num_winners, len(contestants)))
                state["winners"] = picked
                state["is_drawing"] = False
                save_state(state)
                st.rerun()

# --- Main Interface ---
st.title("🦆 Shooting Club Draw")

if state.get("is_drawing"):
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
    st.header("🥁 DRUMROLL... SHUFFLING ENTRIES!")
    st.spinner("The hunt is on...")
    time.sleep(2)
    st.rerun()

elif state.get("winners"):
    st.header("🏆 The Official Winners")
    for i, winner in enumerate(state["winners"]):
        st.subheader(f"Rank #{i+1}: **{winner}**")
        time.sleep(1.2)
        st.snow()
    
    st.markdown("---")
    with st.expander("Show Entry List for this Round", expanded=True):
        st.write(", ".join(state["participants"]))

else:
    st.markdown(f"""
        <div class="welcome-container">
            <h1 style="font-size: 80px; margin-bottom: 0;">Welcome To The Draw</h1>
            <p style="font-size: 30px; opacity: 0.7;">{state.get('last_init', 'Ready to Begin')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if state.get("participants"):
        st.markdown("---")
        with st.expander("Current Round Contestants", expanded=True):
            st.write(", ".join(state["participants"]))

time.sleep(10)
st.rerun()
