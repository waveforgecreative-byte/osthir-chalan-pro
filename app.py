import streamlit as st
import os
import json
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

# --- PREMIUM PAGE CONFIG ---
st.set_page_config(page_title="অস্থির চালান PRO", page_icon="⚡", layout="wide")

# --- DATABASE FILES (LOCAL JSON) ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
HISTORY_DB = "users_history_memory.json" # ইউজারের ইউনিক মেমোরি ফাইল

def load_db():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_db(data):
    with open(USER_DB, "w") as f: json.dump(data, f, indent=4)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    return {"master_pin": "69", "admin_pass": "reyadh123", "serp_api_key": ""}

def save_config(config):
    with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)

def load_history():
    if os.path.exists(HISTORY_DB):
        with open(HISTORY_DB, "r") as f: return json.load(f)
    return {}

def save_history(data):
    with open(HISTORY_DB, "w") as f: json.dump(data, f, indent=4)

users = load_db()
config = load_config()

# --- PREMIUM CYBERBLUE CSS ---
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
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- AUTHENTICATION INTERFACE ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">⚡ অস্থির চালান PRO</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Secure Portal Access Gate</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔑 Get Access Info")
        if st.button("📢 Click to View Notice Board"):
            st.markdown(f'<div class="notice-box">📢 নোটিশ বোর্ড:<br>এই ওয়েবসাইটের এক্সেস পাইতে হইলে রিয়াদ ভাইকে মেসেজ দিয়া ২ ডিজিটের পিন চান 😂</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📝 Create User ID")
        new_username = st.text_input("Choose Unique User ID / Your Name:", key="reg_user")
        if st.button("Create Account & Save"):
            if new_username.strip() == "": st.error("User ID ফাঁকা রাখা যাবে না!")
            elif new_username in users: st.warning("এই নামে অলরেডি আইডি আছে!")
            else:
                users[new_username] = {"status": "pending"}
                save_db(users)
                st.success("✅ আইডি ক্রিয়েট হয়েছে! এখন ডানপাশে পিন দিয়ে লগইন করুন।")
                
    with col2:
        st.markdown("### 🔓 Enter Secure Pin to Access")
        login_username = st.text_input("Enter Registered User ID:", key="login_user")
        input_pin = st.text_input("Enter 2-Digit Secret Access Pin:", type="password", key="login_pin")
        
        if st.button("Unlock Website & Enter 🚀"):
            if login_username not in users: st.error("❌ এই ইউজার আইডিটি পাওয়া যায়নি!")
            elif input_pin != config["master_pin"]: st.error("❌ ভুল এক্সেস পিন!")
            else:
                st.session_state.logged_in_user = login_username
                st.rerun()

# --- MAIN APP INTERFACE (WHEN LOGGED IN) ---
else:
    current_user_id = st.session_state.logged_in_user
    
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f'<p class="main-title">⚡ অস্থির চালান PRO</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#38BDF8; font-weight:600;">Active Session: {current_user_id} (Authorized)</p>', unsafe_allow_html=True)
    with c2:
        if st.button("Log Out 🚪"):
            st.session_state.logged_in_user = None
            st.rerun()
            
    # --- LIVE EMAIL EXTRACTOR ENGINE ---
    def extract_real_email_from_web(url):
        if not url or url == "N/A" or "google.com" in url: return "No"
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get(url, headers=headers, timeout=5)
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, res.text)
            
            # ফিল্টারিং ইমেজ/ফাইল এক্সটেনশন ইমেইল
            valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
            if valid_emails:
                return valid_emails[0] # প্রথম ভ্যালিড মেইলটা রিটার্ন করবে
        except:
            pass
        return "No"

    # --- SERPAPI REAL DATA HUNTING CORE ---
    def start_real_serp_hunting(search_query, status_box, table_placeholder, user_id):
        api_key = config.get("serp_api_key", "").strip()
        if not api_key:
            status_box.error("❌ এডমিন প্যানেলে SerpApi Key সেট করা নাই! রিয়াদ ভাইকে বলেন এপিআই কী বসাতে।")
            return []
            
        # ইউজারের আগের হিস্টোরি চেক করা
        history = load_history()
        if user_id not in history:
            history[user_id] = []
            
        user_scraped_memory = set(history[user_id])
        
        status_box.info(f"🚀 Connecting to SerpApi Cloud & Crawling Live Websites for: '{search_query}'...")
        
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_maps",
            "q": search_query,
            "type": "search",
            "api_key": api_key,
            "start": 0 # প্রথম পেজ থেকে খোঁজা শুরু করবে
        }
        
        leads = []
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            local_results = data.get("local_results", [])
            
            if not local_results:
                status_box.warning("⚠️ গুগল ম্যাপসে এই সার্চের কোনো নতুন রিয়েল ডাটা পাওয়া যায়নি।")
                return []
                
            for place in local_results:
                place_id = place.get("data_id", place.get("title")) # ইউনিক আইডি ট্র্যাকিং
                
                # যদি এই ইউজার আইডি অলরেডি এটা স্ক্র্যাপ করে থাকে, তবে স্কিপ (নতুন ডেটা আসবে)
                if place_id in user_scraped_memory:
                    continue
                
                website = place.get("website", "N/A")
                
                # লাইভ ওয়েবসাইট থেকে আসল ইমেইল খোঁজা
                status_box.info(f"🔎 Scanning website for: {place.get('title')}...")
                email = extract_real_email_from_web(website)
                
                leads.append({
                    "Client Name": place.get("title", "N/A"),
                    "Number": place.get("phone", "N/A"),
                    "Website": website,
                    "Address": place.get("address", "N/A"),
                    "Rating": place.get("rating", "N/A"),
                    "Email": email
                })
                
                # ইউজারের মেমোরিতে এই ডেটা সেভ করে রাখা যাতে পরে আর না আসে
                history[user_id].append(place_id)
                
                # Live Rendering Table
                df_current = pd.DataFrame(leads)
                table_placeholder.dataframe(df_current, use_container_width=True)
                
            save_history(history) # ডাটাবেজে মেমোরি রাইট করা হলো
                
        except Exception as e:
            status_box.error(f"Error connecting to cloud: {str(e)}")
            
        return leads

    # --- UI SEARCH PANEL ---
    search_keyword = st.text_input("Enter Niche & Location:", placeholder="e.g., Dental Clinic in New York")
    submit_btn = st.button("LAUNCH REAL-TIME MOVEMENT CORE 🚀")
    
    status_box = st.empty()
    table_placeholder = st.empty()

    if submit_btn and search_keyword:
        results = start_real_serp_hunting(search_keyword, status_box, table_placeholder, current_user_id)
        if results:
            status_box.success(f"🔥 Successfully Fetched {len(results)} FRESH & UNIQUE Leads from Google Maps Cloud!")
            df_final = pd.DataFrame(results)
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer: df_final.to_excel(writer, index=False)
            st.download_button(label="Download Unique Leads Sheet (.xlsx) 📥", data=buffer.getvalue(), file_name=f"Fresh_Leads_{search_keyword.replace(' ', '_')}.xlsx")
        else:
            status_box.warning("🔄 আপনার এই আইডির জন্য কোনো নতুন ডাটা পাওয়া যায়নি! অন্য নিশ ট্রাই করুন।")

# --- REYADH BHAI's GOD-MODE ADMIN PANEL ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Reyadh Bhai's Secret Control Room"):
    admin_auth = st.text_input("Enter Secret Admin Password:", type="password", key="admin_auth_pass")
    if admin_auth == config["admin_pass"]:
        st.success("Welcome Back, Owner MD Reyadh! God-Mode Activated.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 👥 Manage Active Users")
            current_users = list(users.keys())
            if not current_users:
                st.info("কোনো ইউজার নাই।")
            else:
                for u in current_users:
                    col_u, col_b = st.columns([3, 1])
                    col_u.text(f"👤 User: {u}")
                    if col_b.button("Delete User ❌", key=f"del_{u}"):
                        del users[u]
                        save_db(users)
                        st.success(f"User '{u}' deleted!")
                        st.rerun()
        with c2:
            st.markdown("### ⚙️ System Config & API Gateway")
            st.write(f"**Current Access Pin:** `{config['master_pin']}`")
            new_pin = st.text_input("Set New 2-Digit Pin:", max_chars=4)
            if st.button("Change Pin"):
                if new_pin.strip() != "":
                    config["master_pin"] = new_pin
                    save_config(config)
                    st.success("পিন চেঞ্জড!")
                    st.rerun()
            
            st.markdown("---")
            st.write("**🔑 SerpApi Cloud Key Configuration:**")
            current_key = config.get("serp_api_key", "")
            masked_key = f"{current_key[:5]}...{current_key[-5:]}" if len(current_key) > 10 else "Not Set"
            st.write(f"Active Key Status: `{masked_key}`")
            new_key = st.text_input("Paste Your SerpApi Key here:", type="password")
            if st.button("Save API Key 💾"):
                if new_key.strip() != "":
                    config["serp_api_key"] = new_key
                    save_config(config)
                    st.success("💥 API Key successfully linked to Cloud Engine!")
                    st.rerun()
                    
    elif admin_auth != "":
        st.error("ভুল এডমিন পাসওয়ার্ড!")

st.markdown('<div class="footer">Osthir Chalan Engine v6.0 | Handcrafted by <span>MD Reyadh</span></div>', unsafe_allow_html=True)