import streamlit as st
import os
import json
import requests
import pandas as pd

# --- PREMIUM PAGE CONFIG ---
st.set_page_config(page_title="অস্থির চালান PRO", page_icon="⚡", layout="wide")

# --- CLOUD SAFE DATABASE MECHANISM ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
HISTORY_DB = "users_history_memory.json"

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f: return json.load(f)
        except: return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# সেশন স্টেট মেমোরি ব্যাকআপ (ক্লাউড সেফটি)
if "users_cache" not in st.session_state:
    st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state:
    st.session_state.config_cache = load_json_file(CONFIG_FILE, {"master_pin": "69", "admin_pass": "reyadh123", "serp_api_key": ""})
if "history_cache" not in st.session_state:
    st.session_state.history_cache = load_json_file(HISTORY_DB, {})

users = st.session_state.users_cache
config = st.session_state.config_cache
history = st.session_state.history_cache

# --- PREMIUM CYBERBLUE CSS (WITH MENU HIDING MAGIC) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght=500;700&family=Plus+Jakarta+Sans:wght=400;600;700;800&display=swap');
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0A0F1D; color: #F1F5F9;
    }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 50px !important; font-weight: 800 !important; background: linear-gradient(135deg, #38BDF8 0%, #1D4ED8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .sub-title { color: #64748B; font-size: 15px; margin-bottom: 30px; }
    .notice-box { background: rgba(56, 189, 248, 0.1); border: 1px solid #38BDF8; padding: 20px; border-radius: 12px; font-family: 'Hind Siliguri', sans-serif !important; font-size: 18px; color: #38BDF8; text-align: center; margin-bottom: 20px; line-height: 1.6; }
    div.stTextInput > div > div > input { background-color: #141B2D !important; color: #FFFFFF !important; border: 1px solid #1E293B !important; border-radius: 12px !important; padding: 12px !important; }
    div.stButton > button { background: linear-gradient(135deg, #0284C7 0%, #1E40AF 100%) !important; color: #FFFFFF !important; border-radius: 12px !important; font-weight: 700; padding: 14px 30px !important; border: none !important; width: 100%; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3); }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4); }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0A0F1D; color: #475569; text-align: center; padding: 12px; font-size: 13px; border-top: 1px solid #1E293B; z-index: 999; }
    .footer span { color: #38BDF8; font-weight: 700; }
    
    /* STREAMLIT DEFAULT ICON & MENU HIDING INJECTOR */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stAppDeployDropdown {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    .stActionButton {display: none !important;}
    </style>
""", unsafe_allow_html=True)
