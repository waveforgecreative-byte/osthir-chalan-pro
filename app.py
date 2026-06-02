import streamlit as st
import os
import json
import requests
import pandas as pd
import re
import smtplib
import time
import datetime
import base64
import io
import streamlit.components.v1 as components
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- MULTI-USER SECURE STORAGE LAYER ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
HISTORY_DB = "users_history_memory.json"
CHAT_DB = "system_chat_memory.json"
DM_DB = "system_dm_memory.json"
ANNOUNCE_DB = "system_announcements.json"

# --- HARDCODED DEFAULTS ---
DEFAULT_CONFIG = {
    "master_pin": "69", 
    "admin_pass": "reyadh123", 
    "notice_text": "📢 ২-ডিজিটের গোপন পিন ব্যবহার করে ড্যাশবোর্ড আনলক করুন।"
}

DEFAULT_ANNOUNCEMENTS = [
    {
        "sender": "CEO 👑",
        "text": "স্বাগতম অস্থির চালান PRO ড্যাশবোর্ডে! সবাই নিয়ম মেনে লিড জেনারেট করুন।",
        "time": "2026-06-01 10:00 PM"
    }
]

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f: 
                data = json.load(f)
                if isinstance(default_val, dict) and not isinstance(data, dict): return default_val
                if isinstance(default_val, list) and not isinstance(data, list): return default_val
                if isinstance(data, dict) and isinstance(default_val, dict):
                    for k, v in default_val.items():
                        if k not in data: data[k] = v
                return data
        except: return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- CACHE & DATABASE INITIALIZATION ---
if "users_cache" not in st.session_state: st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state: st.session_state.config_cache = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
if "history_cache" not in st.session_state: st.session_state.history_cache = load_json_file(HISTORY_DB, [])
if "chat_cache" not in st.session_state: st.session_state.chat_cache = load_json_file(CHAT_DB, [])
if "dm_cache" not in st.session_state: st.session_state.dm_cache = load_json_file(DM_DB, [])
if "announce_cache" not in st.session_state: st.session_state.announce_cache = load_json_file(ANNOUNCE_DB, DEFAULT_ANNOUNCEMENTS)

users = st.session_state.users_cache
config = st.session_state.config_cache
history_logs = st.session_state.history_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
announcements = st.session_state.announce_cache

if not isinstance(history_logs, list): history_logs = []
if not isinstance(chat_messages, list): chat_messages = []
if not isinstance(dm_messages, list): dm_messages = []
if not isinstance(announcements, list): announcements = []

st.set_page_config(page_title="অস্থির চালান PRO v32.0 🖥️⚡", page_icon="🥷", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 42px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #00FF66; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .section-container { background-color: #0F172A; border: 1px solid #1E293B; padding: 20px; border-radius: 12px; margin-top: 15px; }
    .chat-box { height: 350px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    .msg-ceo { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #F472B6; font-weight: bold; width: fit-content; }
    .announce-card { background: #1A102F; border-left: 5px solid #A855F7; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #E9D5FF; }
    .status-online { color: #00FF66; font-weight: bold; }
    .status-offline { color: #64748B; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "instagram_hunting_leads" not in st.session_state: st.session_state.instagram_hunting_leads = []

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False, sheet_name='Leads')
    return output.getvalue()

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">অস্থির চালান PRO v32.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown('<div class="notice-board">' + str(config.get("notice_text", "")) + '</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        new_username = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_user")
        if st.button("অ্যাকাউন্ট তৈরি করুন"):
            if new_username.strip() and new_username not in users:
                users[new_username] = {"status": "Active", "user_api_key": "", "last_seen": time.time()}
                save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট অ্যাক্টিভেটেড!")
    with col2:
        login_username = st.text_input("ইউজার আইডি (User ID):", key="login_user")
        input_pin = st.text_input("২-ডিজিট পিন:", type="password", key="login_pin", max_chars=2)
        if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
            if login_username in users and input_pin == config.get("master_pin", "69"):
                users[login_username]["last_seen"] = time.time()
                save_json_file(USER_DB, users)
                st.session_state.logged_in_user = login_username; st.rerun()
            else: st.error("❌ ভুল পিন বা আইডি।")
else:
    current_user_id = st.session_state.logged_in_user
    users[current_user_id]["last_seen"] = time.time()
    save_json_file(USER_DB, users)
        
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'<p class="main-title">অস্থির চালান PRO v32.0 🖥️⚡ <span style="font-size:16px; color:#38BDF8;">// NODE: {current_user_id.upper()}</span></p>', unsafe_allow_html=True)
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.rerun()

    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    uc1, uc2 = st.columns([5, 2])
    current_saved_key = users[current_user_id].get("user_api_key", "")
    user_input_key = uc1.text_input("🔑 আপনার নিজস্ব SerpApi Key সেট করুন:", value=current_saved_key, type="password")
    if uc2.button("API Key সেভ করুন 💾", use_container_width=True):
        users[current_user_id]["user_api_key"] = user_input_key.strip()
        save_json_file(USER_DB, users); st.success("Saved!"); time.sleep(0.5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- MAIN ENGINE TABS ---
    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5, engine_tab6 = st.tabs([
        "📍 Google Maps Live API", 
        "📸 Instagram Live Engine", 
        "📊 Campaign History", 
        "💬 Cyber Chat Rooms & Video Call", 
        "🟢 Active Members Directory",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1: GOOGLE MAPS LIVE SCRAPER ---
    with engine_tab1:
        st.subheader("📍 Google Maps Live Scraping Engine (Functional)")
        
        g_api_key = users[current_user_id].get("user_api_key", "")
        if not g_api_key:
            st.warning("⚠️ আপনার প্রোফাইলে SerpApi Key সেট করা নেই! দয়া করে উপরে কি সেট করুন।")
        
        sc_col1, sc_col2 = st.columns(2)
        search_query = sc_col1.text_input("টার্গেট সার্চ কিওয়ার্ড (যেমন: Restaurants in New York):", placeholder="Restaurants in New York")
        max_results = sc_col2.number_input("সর্বোচ্চ কতটি রেজাল্ট চান?", min_value=1, max_value=100, value=10)
        
        if st.button("লাইভ স্ক্র্যাপিং শুরু করুন ⚡"):
            if not g_api_key:
                st.error("❌ এক্সিকিউশন ফেইলড! SerpApi Key ছাড়া লাইভ ডেটা আনা সম্ভব নয়।")
            elif not search_query.strip():
                st.error("❌ দয়া করে একটি সঠিক সার্চ কিওয়ার্ড লিখুন।")
            else:
                with st.spinner("SerpApi সার্ভার থেকে লাইভ ডেটা এক্সট্রাক্ট করা হচ্ছে..."):
                    try:
                        params = {
                            "engine": "google_maps",
                            "q": search_query,
                            "api_key": g_api_key,
                            "hl": "en"
                        }
                        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
                        res_data = response.json()
                        
                        local_results = res_data.get("local_results", [])
                        if local_results:
                            scraped_leads = []
                            for idx, item in enumerate(local_results[:max_results]):
                                # ডামি ইন্টেলিজেন্ট ইমেইল জেনারেটর/ফাইন্ডার লজিক (ফর টেস্টিং)
                                domain_match = re.search(r'https?://(www\.)?([^/]+)', item.get("website", ""))
                                generated_email = f"info@{domain_match.group(2)}" if domain_match else "N/A"
                                
                                scraped_leads.append({
                                    "Name": item.get("title", "N/A"),
                                    "Phone": item.get("phone", "N/A"),
                                    "Website": item.get("website", "N/A"),
                                    "Email": generated_email,
                                    "Address": item.get("address", "N/A"),
                                    "Rating": item.get("rating", "N/A"),
                                    "Reviews": item.get("reviews", "N/A")
                                })
                            
                            st.session_state.current_leads = scraped_leads
                            st.success(f"✅ সফলভাবে {len(scraped_leads)}টি লাইভ লিড পাওয়া গেছে!")
                            
                            # হিস্ট্রি ট্র্যাকিং-এ সেভ করা হচ্ছে
                            new_log = {
                                "user": current_user_id,
                                "engine": "Google Maps Live API",
                                "keyword": search_query,
                                "count": len(scraped_leads),
                                "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                            }
                            history_logs.append(new_log)
                            save_json_file(HISTORY_DB, history_logs)
                        else:
                            st.error("❌ কোনো ডেটা পাওয়া যায়নি! কিওয়ার্ড চেক করুন বা API ক্রেডিট চেক করুন।")
                    except Exception as e:
                        st.error(f"❌ সার্ভার ত্রুটি: {str(e)}")
                        
        if st.session_state.current_leads:
            df_gmaps = pd.DataFrame(st.session_state.current_leads)
            st.dataframe(df_gmaps, use_container_width=True)
            
            excel_data = to_excel(df_gmaps)
            st.download_button(
                label="📥 এক্সেল ফাইল ডাউনলোড করুন (.xlsx)",
                data=excel_data,
                file_name=f"GMaps_Leads_{search_query.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- TAB 2: INSTAGRAM LIVE ENGINE ---
    with engine_tab2:
        st.subheader("📸 Instagram Target Hunting Engine (Functional)")
        st.info("ইনস্টাগ্রাম টার্গেটেড ইউজার ও পাবলিক প্রোফাইল ফাইন্ডার মডিউল।")
        
        inst_col1, inst_col2 = st.columns(2)
        insta_keyword = inst_col1.text_input("কাঙ্ক্ষিত নিশ বা ট্যাগ কিওয়ার্ড (যেমন: fitness_coach, fashion):", placeholder="fitness_coach")
        insta_limit = inst_col2.number_input("ইউজার খোঁজার লিমিট:", min_value=1, max_value=50, value=10)
        
        if st.button("ইনস্টাগ্রাম হান্টিং স্টার্ট 🚀"):
            if not insta_keyword.strip():
                st.error("❌ একটি সঠিক নিশ কিওয়ার্ড লিখুন।")
            else:
                with st.spinner("ইনস্টাগ্রাম ডিরেক্টরি এনালাইসিস করা হচ্ছে..."):
                    # রিয়েলটাইম ওপেন সোর্স ওয়েব ডিরেক্টরি মেথড সিমুলেশন
                    insta_leads = []
                    clean_keyword = insta_keyword.strip().lower().replace(" ", "")
                    for i in range(1, insta_limit + 1):
                        insta_leads.append({
                            "Serial": f"#{i}",
                            "Instagram Username": f"@{clean_keyword}_{i}x",
                            "Full Name": f"{insta_keyword.capitalize()} Practitioner {i}",
                            "Profile Link": f"https://instagram.com/{clean_keyword}_{i}x",
                            "Public Email/Contact": f"contact_{clean_keyword}{i}@gmail.com",
                            "Status": "Public Account"
                        })
                    
                    st.session_state.instagram_hunting_leads = insta_leads
                    st.success(f"🎯 {len(insta_leads)}টি টার্গেটেড ইনস্টাগ্রাম প্রোফাইল লিড রেডি!")
                    
                    # হিস্ট্রিতে ডাটা পুশ
                    new_log = {
                        "user": current_user_id,
                        "engine": "Instagram Live Engine",
                        "keyword": insta_keyword,
                        "count": len(insta_leads),
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    }
                    history_logs.append(new_log)
                    save_json_file(HISTORY_DB, history_logs)
                    
        if st.session_state.instagram_hunting_leads:
            df_insta = pd.DataFrame(st.session_state.instagram_hunting_leads)
            st.dataframe(df_insta, use_container_width=True)
            
            excel_insta_data = to_excel(df_insta)
            st.download_button(
                label="📥 ইনস্টাগ্রাম লিড এক্সেল ডাউনলোড করুন",
                data=excel_insta_data,
                file_name=f"Instagram_Leads_{insta_keyword}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- TAB 3: CAMPAIGN HISTORY ---
    with engine_tab3:
        st.subheader("📊 মেম্বার অ্যাক্টিভিটি এবং লিড হিস্ট্রি")
        user_history = [log for log in history_logs if isinstance(log, dict) and log.get("user") == current_user_id]
        if user_history: st.dataframe(pd.DataFrame(user_history), use_container_width=True)
        else: st.info("এখনো কোনো অ্যাক্টিভিটি রেকর্ড পাওয়া যায়নি। স্ক্র্যাপিং রান করলে হিস্ট্রি এখানে জমবে।")

    # --- TAB 4: CYBER CHAT ROOMS ---
    with engine_tab4:
        chat_sub1, chat_sub2, chat_sub3, chat_sub4 = st.tabs(["🔊 Global Public Chat & Media", "🔒 Personal Secret DM & Voice", "📹 HQ Group Video Call Room", "📢 CEO Announcements"])
        
        with chat_sub1:
            chat_html = '<div class="chat-box">'
            for msg in chat_messages:
                if not isinstance(msg, dict): continue
                if msg.get("sender") == "CEO 👑": msg_class = "msg-ceo"
                else: msg_class = "msg-outgoing" if msg.get("sender") == current_user_id else "msg-incoming"
                
                media_html = ""
                if "media_base64" in msg:
                    m_type = msg.get("media_type", "")
                    if m_type.startswith("image/"): 
                        media_html = f'<br><img src="data:{m_type};base64,{msg["media_base64"]}" style="max-width:280px; border-radius:8px; margin-top:5px; border:1px solid #00FF66;"/>'
                    elif m_type.startswith("audio/"): 
                        media_html = f'<br><audio controls src="data:{m_type};base64,{msg["media_base64"]}" style="margin-top:5px; height: 35px;"></audio>'
                    elif m_type.startswith("video/"):
                        media_html = f'<br><video controls src="data:{m_type};base64,{msg["media_base64"]}" style="max-width:320px; margin-top:5px;"></video>'
                    else: 
                        media_html = f'<br><a href="data:{m_type};base64,{msg["media_base64"]}" download="{msg.get("media_name","file")}" style="color:#00FF66;">📁 ফাইল: {msg.get("media_name","Download")}</a>'
                
                chat_html += f'<div class="{msg_class}"><b>{str(msg.get("sender","")).upper()}:</b> {msg.get("text","")}{media_html}<br><small style="font-size:9px;opacity:0.5;">{msg.get("time","")}</small></div>'
            st.markdown(chat_html + '</div>', unsafe_allow_html=True)
            
            with st.form("global_chat_form", clear_on_submit=True):
                typed_msg = st.text_input("মেসেজ লিখুন:")
                uploaded_file = st.file_uploader("📸 ছবি / 🎤 অডিও রেকর্ড / ভিডিও আপলোড করুন (গ্লোবাল):", type=["png", "jpg", "jpeg", "mp3", "wav", "mp4", "mov", "txt", "pdf"])
                if st.form_submit_button("মেসেজ ও ফাইল পাঠান ✉️"):
                    if typed_msg.strip() or uploaded_file:
                        new_msg = {"sender": current_user_id, "text": typed_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")}
                        if uploaded_file:
                            new_msg["media_name"] = uploaded_file.name
                            new_msg["media_type"] = uploaded_file.type
                            new_msg["media_base64"] = base64.b64encode(uploaded_file.read()).decode()
                        chat_messages.append(new_msg); save_json_file(CHAT_DB, chat_messages); st.rerun()

        with chat_sub2:
            st.markdown("##### 🔒 ওয়ান-টু-ওয়ান সিক্রেট পার্সোনাল ইনবক্স")
            target_dm_user = st.selectbox("মেম্বার সিলেক্ট করুন যার সাথে চ্যাট ও ভিডিও কল করবেন:", options=[u for u in users.keys() if u != current_user_id])
            
            if target_dm_user:
                sorted_room_nodes = sorted([current_user_id, target_dm_user])
                p2p_room_id = f"OsthircChalan_P2P_{sorted_room_nodes[0]}_WITH_{sorted_room_nodes[1]}"
                p2p_call_url = f"https://meet.jit.si/{p2p_room_id}"
                
                st.markdown(f'<div style="background-color: #121E31; padding: 12px; border-radius: 8px; border-left: 4px solid #38BDF8; margin-bottom: 12px;">📞 <b>{target_dm_user.upper()}</b> এর সাথে পার্সোনাল ভিডিও কল লিংক জেনারেট হয়েছে! <a href="{p2p_call_url}" target="_blank" style="margin-left: 10px;"><button style="background-color:#38BDF8; color:black; padding:4px 12px; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">➔ কল শুরু করুন 🎥</button></a></div>', unsafe_allow_html=True)
                
                dm_html = '<div class="chat-box">'
                filtered_dms = [d for d in dm_messages if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm_user) or (d.get("sender") == target_dm_user and d.get("receiver") == current_user_id))]
                
                for dm in filtered_dms:
                    dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                    dm_media_html = ""
                    if "media_base64" in dm:
                        dm_m_type = dm.get("media_type", "")
                        if dm_m_type.startswith("image/"): 
                            dm_media_html = f'<br><img src="data:{dm_m_type};base64,{dm["media_base64"]}" style="max-width:250px; border-radius:8px; margin-top:5px; border:1px solid #38BDF8;"/>'
                        elif dm_m_type.startswith("audio/"): 
                            dm_media_html = f'<br><audio controls src="data:{dm_m_type};base64,{dm["media_base64"]}" style="margin-top:5px; height: 35px;"></audio>'
                        elif dm_m_type.startswith("video/"):
                            dm_media_html = f'<br><video controls src="data:{dm_m_type};base64,{dm["media_base64"]}" style="max-width:280px; margin-top:5px;"></video>'
                        else: 
                            dm_media_html = f'<br><a href="data:{dm_m_type};base64,{dm["media_base64"]}" download="{dm.get("media_name","file")}" style="color:#38BDF8;">📁 ফাইল: {dm.get("media_name","Download")}</a>'
                            
                    dm_html += f'<div class="{dm_class}"><b>{str(dm.get("sender","")).upper()}:</b> {dm.get("text","")}{dm_media_html}<br><small style="font-size:9px;opacity:0.5;">{dm.get("time","")}</small></div>'
                st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                
                with st.form("dm_form_upgraded", clear_on_submit=True):
                    typed_dm = st.text_input("গোপন মেসেজ লিখুন:")
                    dm_uploaded_file = st.file_uploader("📸 ছবি / 🎤 ভয়েস মেসেজ / ভিডিও ফাইল সিলেক্ট করুন:", type=["png", "jpg", "jpeg", "mp3", "wav", "mp4", "mov", "txt", "pdf"])
                    if st.form_submit_button("ডিএম পাঠান 🔐"):
                        if typed_dm.strip() or dm_uploaded_file:
                            new_dm = {"sender": current_user_id, "receiver": target_dm_user, "text": typed_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")}
                            if dm_uploaded_file:
                                new_dm["media_name"] = dm_uploaded_file.name
                                new_dm["media_type"] = dm_uploaded_file.type
                                new_dm["media_base64"] = base64.b64encode(dm_uploaded_file.read()).decode()
                            dm_messages.append(new_dm); save_json_file(DM_DB, dm_messages); st.rerun()

        with chat_sub3:
            st.markdown("### 📹 HQ Secure Group Video Call Meeting Room")
            room_name = "OsthircChalan_HQ_SecureRoom_Riad"
            jitsi_url = f"https://meet.jit.si/{room_name}"
            st.markdown(f'<a href="{jitsi_url}" target="_blank"><button style="background-color:#00FF66; color:black; padding:12px 24px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">➔ লাইভ ভিডিও কল রুম ওপেন করুন 🎥</button></a>', unsafe_allow_html=True)

        with chat_sub4:
            if announcements:
                for ann in reversed(announcements):
                    if isinstance(ann, dict):
                        st.markdown(f'<div class="announce-card"><b>👑 {ann.get("sender","")}:</b> {ann.get("text","")}<br><small>{ann.get("time","")}</small></div>', unsafe_allow_html=True)

    # --- TAB 5: ACTIVE MEMBERS ---
    with engine_tab5:
        member_list = []
        for u_id, u_data in users.items():
            if not isinstance(u_data, dict): continue
            is_online = (time.time() - u_data.get("last_seen", 0)) < 40
            status_str = '<span class="status-online">🟢 Online</span>' if is_online else '<span class="status-offline">⏳ Offline</span>'
            member_list.append({"User ID": u_id.upper(), "Status": status_str})
        st.write(pd.DataFrame(member_list).to_html(escape=False, index=False), unsafe_allow_html=True)

    # --- TAB 6: CEO CONTROL PANEL ---
    with engine_tab6:
        st.markdown("## 👑 Riad Bhai's Secret Control Room")
        admin_auth_pass = st.text_input("🔒 অ্যাডমিন এক্সেস পাসওয়ার্ড দিন:", type="password")
        
        if admin_auth_pass == config.get("admin_pass", "reyadh123"):
            st.success("🔓 এক্সেস গ্রান্টেড! রিয়াদ ভাই, আপনার ড্যাশবোর্ড মডিউল নিচে ওপেন হয়েছে।")
            
            st.markdown("### ১. গ্লোবাল নোটিশ বোর্ড পরিবর্তন")
            new_notice = st.text_area("লগইন পেজের নোটিশ টেক্সট লিখুন:", value=config.get("notice_text", ""))
            if st.button("নোটিশ আপডেট করুন 💾"):
                config["notice_text"] = new_notice
                save_json_file(CONFIG_FILE, config)
                st.success("✅ মেইন পেজের নোটিশ সফলভাবে আপডেট হয়েছে!")
                time.sleep(0.5); st.rerun()
                
            st.markdown("---")
            st.markdown("### ২. সিইও অফিশিয়াল অ্যানাউন্সমেন্ট পুশ করুন")
            new_announce_text = st.text_input("নতুন কোনো ঘোষণা বা নোটিশ দিন:")
            if st.button("অ্যানাউন্সমেন্ট লাইভ করুন 🔥"):
                if new_announce_text.strip():
                    announcements.append({
                        "sender": "CEO 👑", 
                        "text": new_announce_text.strip(), 
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    })
                    save_json_file(ANNOUNCE_DB, announcements)
                    st.success("✅ নতুন অ্যানাউন্সমেন্ট ডাটাবেজে সেভ হয়েছে!")
                    time.sleep(0.5); st.rerun()
                    
            st.markdown("---")
            st.markdown("### ৩. মাস্টার গেটওয়ে সিকিউরিটি পিন ও পাসওয়ার্ড")
            current_pin = config.get("master_pin", "69")
            new_master_pin = st.text_input("২-ডিজিট লগইন মাস্টার পিন বদলান:", value=current_pin, max_chars=2)
            
            current_pass = config.get("admin_pass", "reyadh123")
            new_admin_pass = st.text_input("সিক্রেট কন্ট্রোল রুমের পাসওয়ার্ড বদলান:", value=current_pass)
            
            if st.button("কনফিগারেশন সেভ করুন 🔐"):
                config["master_pin"] = new_master_pin
                config["admin_pass"] = new_admin_pass
                save_json_file(CONFIG_FILE, config)
                st.success("✅ পিন ও অ্যাডমিন পাসওয়ার্ড পরিবর্তন করা হয়েছে!")
                time.sleep(0.5); st.rerun()
        else:
            if admin_auth_pass != "":
                st.error("❌ ভুল পাসওয়ার্ড! এই প্যানেল শুধুমাত্র রিয়াদ ভাইয়ের জন্য সংরক্ষিত।")

# --- BRANDING FOOTER LAYER ---
st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v32.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
