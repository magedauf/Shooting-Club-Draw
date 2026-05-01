import streamlit as st
import random
import json
import os
import time

# --- Persistence ---
STATE_FILE = "raffle_state.json"
NAMES_FILE = "names.txt"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"winners": [], "bg_opacity": 0.5, "is_drawing": False, "participants": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_names():
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

state = load_state()
master_names = load_names()

# --- Custom Styling & Branding ---
st.set_page_config(page_title="Shooting Club Draw", page_icon="🎯", layout="wide")

# This link pulls directly from your public GitHub repository
bg_url = "https://raw.githubusercontent.com/magedauf/Shooting-Club-Draw/main/bg.jpg"
bg_opacity = state.get("bg_opacity", 0.5)

st.markdown(f"""
    <style>
    /* Main background color under the image: Black */
    .stApp {{
        background-color: #000000;
        background: linear-gradient(rgba(0, 0, 0, {1 - bg_opacity}), rgba(0, 0, 0, {1 - bg_opacity})), 
                    url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
    }}
    
    /* Sidebar color: Dark Grey */
    [data-testid="stSidebar"] {{
        background-color: #2c2c2c;
        color: #ffffff;
    }}

    /* Ensuring labels and text in sidebar are white */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{
        color: #ffffff !important;
    }}

    /* Styling the dropdowns and inputs for visibility */
    div[data-baseweb="select"] > div {{
        background-color: #3d3d3d;
        color: white;
    }}
    
    /* Styling info/success boxes for dark theme */
    .stAlert {{
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* Header styling */
    h1, h2, h3 {{
        color: #ffffff !important;
        text-shadow: 2px 2px 4px #000000;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar & Authentication ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.title("🎯 Control Panel")
access = st.sidebar.selectbox("Access Level", ["Visitor", "Admin", "Super Admin"])
pwd = st.sidebar.text_input("Access Key", type="password")

is_super = (access == "Super Admin" and pwd == "maged_super_2026")
is_admin = (access == "Admin" and pwd == "team_admin_2026") or is_super

# --- Super Admin: Styling Controls ---
if is_super:
    st.sidebar.subheader("🎨 Visual Settings")
    new_opacity = st.sidebar.slider("Background Visibility", 0.0, 1.0, float(state.get("bg_opacity", 0.5)))
    if new_opacity != state["bg_opacity"]:
        state["bg_opacity"] = new_opacity
        save_state(state)
        st.rerun()

# --- Admin: Raffle Management ---
if is_admin:
    st.sidebar.divider()
    if st.sidebar.button("🔄 Initialize New Draw"):
        state["winners"] = []
        state["is_drawing"] = False
        state["participants"] = []
        save_state(state)
        st.rerun()

    if not state["winners"]:
        st.sidebar.subheader("📝 Round Setup")
        contestants = st.sidebar.multiselect("Select Contestants", options=master_names, default=master_names)
        num_winners = st.sidebar.selectbox("Number of Winners", range(1, 11), index=0)
        
        if st.sidebar.button("🔥 EXECUTE DRAW"):
            if contestants:
                # 1. Set drawing state for visitors
                state["is_drawing"] = True
                save_state(state)
                
                # 2. Pick unique winners (random.sample avoids duplicates)
                picked = random.sample(contestants, min(num_winners, len(contestants)))
                
                # 3. Save finalized list and stop drawing state
                state["winners"] = picked
                state["participants"] = contestants
                state["is_drawing"] = False
                save_state(state)
                st.rerun()

# --- Main Interface ---
st.title("🏹 Shooting Club Draw")

if state.get("is_drawing"):
    st.header("🥁 DRUMROLL... SHUFFLING NAMES!")
    st.spinner("Randomizing entries...")
    time.sleep(2)
    st.rerun()

elif state["winners"]:
    st.header("🏆 The Official Winners")
    # Sequential reveal for suspense starting from Rank #1
    for i, winner in enumerate(state["winners"]):
        st.subheader(f"Rank #{i+1}: **{winner}**")
        time.sleep(1.2) # Suspension pause
        st.balloons()
    
    with st.expander("Show Entry List for this Round"):
        st.write(", ".join(state["participants"]))
else:
    st.info("👋 Welcome! Please stay on this page. The draw will begin shortly.")
    if master_names:
        with st.expander("View Registered Members"):
            st.write(", ".join(master_names))

# Auto-refresh loop for visitors (every 10 seconds)
time.sleep(10)
st.rerun()
