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

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f: 
                data = json.load(f)
                # বুলেটপ্রুফ টাইপ চেকিং
                if isinstance(default_val, dict) and not isinstance(data, dict):
                    return default_val
                if isinstance(default_val, list) and not isinstance(data, list):
                    return default_val
                
                if isinstance(data, dict) and isinstance(default_val, dict):
                    for k, v in default_val.items():
                        if k not in data:
                            data[k] = v
                return data
        except: 
            return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# INITIAL CACHE CONFIG
DEFAULT_CONFIG = {
    "master_pin": "69", 
    "admin_pass": "ria123", 
    "notice_text": "📢 ২-ডিজিটের গোপন পিন ব্যবহার করে কোর ড্যাশবোর্ড আনলক করুন। পিন না জানলে রিয়াদ ভাইয়ের কাছে ২ ডিজিটের পিন চান ! 😆"
}

if "users_cache" not in st.session_state: st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state: st.session_state.config_cache = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
if "history_cache" not in st.session_state: st.session_state.history_cache = load_json_file(HISTORY_DB, [])
if "chat_cache" not in st.session_state: st.session_state.chat_cache = load_json_file(CHAT_DB, [])
if "dm_cache" not in st.session_state: st.session_state.dm_cache = load_json_file(DM_DB, [])
if "announce_cache" not in st.session_state: st.session_state.announce_cache = load_json_file(ANNOUNCE_DB, [])

users = st.session_state.users_cache
config = st.session_state.config_cache
history_logs = st.session_state.history_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
announcements = st.session_state.announce_cache

# ডাটাবেজ ইন্টিগ্রিটি রি-রেনফোর্সমেন্ট
if not isinstance(history_logs, list): history_logs = []
if not isinstance(chat_messages, list): chat_messages = []
if not isinstance(dm_messages, list): dm_messages = []
if not isinstance(announcements, list): announcements = []

if "notice_text" not in config: config["notice_text"] = DEFAULT_CONFIG["notice_text"]
if "master_pin" not in config: config["master_pin"] = DEFAULT_CONFIG["master_pin"]
if "admin_pass" not in config: config["admin_pass"] = DEFAULT_CONFIG["admin_pass"]

st.set_page_config(page_title="অস্থির চালান PRO v32.0 🖥️⚡", page_icon="🥷", layout="wide")

# PREMIUM CYBERPUNK CSS STYLING
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 42px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #00FF66; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; font-size: 16px; box-shadow: 0 0 15px rgba(0,255,102,0.1); }
    .section-container { background-color: #0F172A; border: 1px solid #1E293B; padding: 20px; border-radius: 12px; margin-top: 15px; }
    .chat-box { height: 350px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; text-align: right; border-right: 3px solid #00FF66; }
    .msg-ceo { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #F472B6; box-shadow: 0 0 8px #F472B6; width: fit-content; max-width: 80%; font-weight: bold; }
    .announce-card { background: #1A102F; border-left: 5px solid #A855F7; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #E9D5FF; border: 1px solid #6B21A8; }
    .alert-card { background: #450A0A; border-left: 5px solid #EF4444; padding: 12px; border-radius: 6px; margin: 10px 0; color: #FFCACA; font-weight: bold; }
    .status-online { color: #00FF66; font-weight: bold; font-size: 13px; }
    .status-offline { color: #64748B; font-size: 12px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; z-index: 99; color: #64748B; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "instagram_hunting_leads" not in st.session_state: st.session_state.instagram_hunting_leads = []
if "email_sent_counter" not in st.session_state: st.session_state.email_sent_counter = 0
if "connected_email" not in st.session_state: st.session_state.connected_email = ""

# --- EXCEL GENERATOR HELPER ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
    return output.getvalue()

# --- SERPAPI LIVE ENGINES ---
def live_google_maps_api(query, api_key, user_id):
    scraped_before = set([log.get("identifier") for log in history_logs if isinstance(log, dict) and log.get("user") == user_id and log.get("type") == "Google Maps"])
    url = "https://serpapi.com/search.json"
    params = {"engine": "google_maps", "q": query, "type": "search", "api_key": api_key}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        results = res.get("local_results", [])
        leads = []
        idx = 1
        for place in results:
            if len(leads) >= 100: break
            web = place.get("website", "N/A")
            if web == "N/A" or web in scraped_before: continue
            
            raw_phone = place.get("phone", "N/A")
            clean_phone = re.sub(r'[^\d+]', '', raw_phone) if raw_phone != "N/A" else "N/A"
            if clean_phone != "N/A" and len(clean_phone) < 9: clean_phone = "N/A"
            
            leads.append({
                "Client Name": place.get("title", f"Target {idx}"),
                "Website": web,
                "Email": "info@" + web.replace("https://","").replace("http://","").split("/")[0],
                "WhatsApp Number": clean_phone,
                "Instagram Profile": "N/A"
            })
            idx += 1
        return leads
    except: return []

def live_instagram_api(keyword, api_key, user_id):
    scraped_before = set([log.get("identifier") for log in history_logs if isinstance(log, dict) and log.get("user") == user_id and log.get("type") == "Instagram Hunter"])
    url = "https://serpapi.com/search.json"
    params = {"engine": "google", "q": f'site:instagram.com "{keyword}" "biography"', "api_key": api_key}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        results = res.get("organic_results", [])
        leads = []
        for item in results:
            if len(leads) >= 20: break
            link = item.get("link", "")
            if "instagram.com/" not in link or link in scraped_before: continue
            username = link.split("instagram.com/")[-1].replace("/", "").split("?")[0]
            snippet = item.get("snippet", "")
            emails = re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z0-9.\-_]+', snippet)
            valid_email = emails[0] if emails else "N/A"
            
            leads.append({
                "Client Name": username.upper(),
                "Website": link,
                "Email": valid_email,
                "WhatsApp Number": "N/A",
                "Instagram Profile": link
            })
        return leads
    except: return []

# --- CORE SYSTEM ACCESS GATEWAY ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">অস্থির চালান PRO v32.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown('<div class="notice-board">' + str(config.get("notice_text", "📢 সিস্টেম সচল আছে।")) + '</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 style='color:#00FF66;'>🔑 নতুন অ্যাকাউন্ট রেজিস্টার</h4>", unsafe_allow_html=True)
        new_username = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_user")
        if st.button("অ্যাকাউন্ট তৈরি করুন"):
            if new_username.strip() and new_username not in users:
                users[new_username] = {"status": "Active", "user_api_key": "", "last_seen": time.time()}
                save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট অ্যাক্টিভেটেড!")
    with col2:
        st.markdown("<h4 style='color:#00FF66;'>🥷 নিরাপদ গেটওয়ে লগইন</h4>", unsafe_allow_html=True)
        login_username = st.text_input("ইউজার আইডি (User ID):", key="login_user")
        input_pin = st.text_input("২-ডিজিট পিন:", type="password", key="login_pin", max_chars=2)
        if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
            if login_username in users and input_pin == config.get("master_pin", "69"):
                users[login_username]["last_seen"] = time.time()
                save_json_file(USER_DB, users)
                st.session_state.logged_in_user = login_username; st.rerun()
            else: st.error("❌ অ্যাক্সেস ডিনাইড! ভুল পিন বা আইডি।")
else:
    current_user_id = st.session_state.logged_in_user
    users[current_user_id]["last_seen"] = time.time()
    save_json_file(USER_DB, users)
        
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'<p class="main-title">অস্থির চালান PRO v32.0 🖥️⚡ <span style="font-size:16px; color:#38BDF8;">// NODE: {current_user_id.upper()}</span></p>', unsafe_allow_html=True)
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.rerun()

    if announcements:
        st.toast(f"📢 CEO 👑: {announcements[-1]['text']}", icon="🔥")

    # --- INDIVIDUAL PER-USER API KEY SETUP BOX ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    uc1, uc2 = st.columns([5, 2])
    current_saved_key = users[current_user_id].get("user_api_key", "")
    user_input_key = uc1.text_input("🔑 আপনার নিজস্ব SerpApi Key সেট করুন (১০০% রিয়াল লাইভ ডেটার জন্য):", value=current_saved_key, type="password")
    if uc2.button("API Key সেভ করুন 💾", use_container_width=True):
        users[current_user_id]["user_api_key"] = user_input_key.strip()
        save_json_file(USER_DB, users); st.success("API Key সফলভাবে লক করা হয়েছে!"); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5 = st.tabs(["📍 Google Maps Live API", "📸 Instagram Live Engine", "📊 Campaign History", "💬 Cyber Chat Rooms", "🟢 Active Members Directory"])

    now_ts = time.time()
    last_scrap_key = f"last_scrap_{current_user_id}"
    elapsed = now_ts - st.session_state.get(last_scrap_key, 0)

    # --- TAB 1: GOOGLE MAPS WITH EXCEL ---
    with engine_tab1:
        st.markdown("<h4>📍 গুগল ম্যাপস API ক্রলার (সর্বোচ্চ ১০০টি ইউনিক ফ্রেশ লিড)</h4>", unsafe_allow_html=True)
        if not users[current_user_id].get("user_api_key", ""):
            st.warning("⚠️ ক্রলিং শুরু করার আগে উপরে আপনার নিজস্ব SerpApi Key যুক্ত করুন!")
        elif elapsed < 300:
            st.markdown(f'<div class="alert-card">⚠️ সিকিউরিটি লক! অ্যান্টি-ব্যান মেকানিজম সচল রয়েছে। আর {int(300-elapsed)} সেকেন্ড পর বাটন রিলিজ হবে।</div>', unsafe_allow_html=True)
        else:
            search_keyword = st.text_input("কীওয়ার্ড এবং লোকেশন দিন (e.g. Gym in Dhaka):")
            if st.button("লাইভ ম্যাপস সার্চ চালু করুন ⚡", key="maps_btn"):
                if search_keyword:
                    st.session_state[last_scrap_key] = time.time()
                    status_box = st.empty().info("আপনার পার্সোনাল API দিয়ে লাইভ ডাটাবেজ ফিল্টার করা হচ্ছে...")
                    leads = live_google_maps_api(search_keyword, users[current_user_id]["user_api_key"], current_user_id)
                    if leads:
                        st.session_state.current_leads = leads; st.rerun()
                    else: status_box.warning("⚠️ কোনো নতুন ইউনিক ডাটা পাওয়া যায়নি।")
        
        if st.session_state.current_leads:
            df_maps = pd.DataFrame(st.session_state.current_leads)
            st.dataframe(df_maps, use_container_width=True)
            excel_data = to_excel(df_maps)
            st.download_button(label="📥 Download Maps Leads Excel Sheet", data=excel_data, file_name=f"Maps_Leads_{datetime.date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # --- TAB 2: INSTAGRAM WITH EXCEL ---
    with engine_tab2:
        st.markdown("<h4>📸 ইনস্টাগ্রাম লাইভ API হান্টার (সর্বোচ্চ ২০টি ইউনিক নিশ লিড)</h4>", unsafe_allow_html=True)
        if not users[current_user_id].get("user_api_key", ""):
            st.warning("⚠️ সার্চ শুরু করার আগে উপরে আপনার নিজস্ব SerpApi Key যুক্ত করুন!")
        elif elapsed < 300:
            st.markdown(f'<div class="alert-card">⚠️ সিকিউরিটি লক! আর {int(300-elapsed)} সেকেন্ড পর বাটন রিলিজ হবে।</div>', unsafe_allow_html=True)
        else:
            ig_keyword = st.text_input("টার্গেট নিশ/কীওয়ার্ড লিখুন:")
            if st.button("ইনস্টাগ্রাম এপিআই run করুন 🔥", key="ig_api_btn"):
                if ig_keyword:
                    st.session_state[last_scrap_key] = time.time()
                    ig_leads = live_instagram_api(ig_keyword, users[current_user_id]["user_api_key"], current_user_id)
                    if ig_leads:
                        st.session_state.instagram_hunting_leads = ig_leads; st.rerun()
                    else: st.warning("⚠️ কোনো নতুন ইউনিক প্রোফাইল ডেটা পাওয়া যায়নি।")
        
        if st.session_state.instagram_hunting_leads:
            df_ig = pd.DataFrame(st.session_state.instagram_hunting_leads)
            st.dataframe(df_ig, use_container_width=True)
            excel_ig = to_excel(df_ig)
            st.download_button(label="📥 Download Instagram Leads Excel Sheet", data=excel_ig, file_name=f"IG_Leads_{datetime.date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # --- TAB 3: CAMPAIGN HISTORY ---
    with engine_tab3:
        st.markdown("<h4>📋 অল-টাইম অ্যাকাউন্ট অ্যাক্টিভিটি হিস্টোরি (ডুপ্লিকেট প্রটেকশন লক)</h4>", unsafe_allow_html=True)
        user_history = [log for log in history_logs if isinstance(log, dict) and log.get("user") == current_user_id]
        if user_history: st.dataframe(pd.DataFrame(user_history)[["date", "time", "keyword", "type", "identifier"]].rename(columns={"identifier": "Unique Target Link"}), use_container_width=True)
        else: st.info("কোনো ডাটা মেমোরি রেকর্ড হয়নি।")

    # --- TAB 4: DUO-CHANNEL CHAT ROOMS & PERSONAL DM BOX ---
    with engine_tab4:
        chat_sub1, chat_sub2, chat_sub3 = st.tabs(["🔊 Global Public Chat", "🔒 Personal DM Box (ওয়ান-টু-ওয়ান)", "📢 CEO Announcements"])
        
        with chat_sub1:
            chat_html = '<div class="chat-box">'
            for msg in chat_messages:
                if not isinstance(msg, dict): continue
                if msg.get("sender") == "CEO 👑": msg_class = "msg-ceo"
                else: msg_class = "msg-outgoing" if msg.get("sender") == current_user_id else "msg-incoming"
                
                media_html = ""
                if "media_base64" in msg:
                    if msg["media_type"].startswith("image"): media_html = f'<br><img src="data:{msg["media_type"]};base64,{msg["media_base64"]}" style="max-width:250px; border-radius:8px; margin-top:5px; border:1px solid #00FF66;"/>'
                    elif msg["media_type"].startswith("audio"): media_html = f'<br><audio controls src="data:{msg["media_type"]};base64,{msg["media_base64"]}" style="margin-top:5px; height: 32px;"></audio>'
                    else: media_html = f'<br><a href="data:{msg["media_type"]};base64,{msg["media_base64"]}" download="{msg["media_name"]}" style="color:#00FF66; font-size:12px;">📁 ফাইল: {msg["media_name"]}</a>'
                
                chat_html += f'<div class="{msg_class}"><b>{str(msg.get("sender", "Unknown")).upper()}:</b> {msg.get("text", "")}{media_html}<br><small style="font-size:9px;opacity:0.6;">{msg.get("time", "")}</small></div>'
            st.markdown(chat_html + '</div>', unsafe_allow_html=True)
            
            with st.form("global_chat_form", clear_on_submit=True):
                typed_msg = st.text_input("গ্লোবাল পাবলিক মেসেজ:")
                uploaded_file = st.file_uploader("ফাইল/ছবি আপলোড:", type=["png", "jpg", "jpeg", "mp3", "wav", "txt", "csv", "json"], key="glob_file")
                if st.form_submit_button("মেসেজ পাঠান ✉️"):
                    if typed_msg.strip() or uploaded_file:
                        new_msg = {"sender": current_user_id, "text": typed_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")}
                        if uploaded_file:
                            new_msg["media_name"] = uploaded_file.name; new_msg["media_type"] = uploaded_file.type
                            new_msg["media_base64"] = base64.b64encode(uploaded_file.read()).decode()
                        chat_messages.append(new_msg); save_json_file(CHAT_DB, chat_messages); st.rerun()

        with chat_sub2:
            st.markdown("<h5>🔒 ওয়ান-টু-ওয়ান সিক্রেট পার্সোনাল ইনবক্স</h5>", unsafe_allow_html=True)
            target_dm_user = st.selectbox("মেম্বার সিলেক্ট করুন যার সাথে চ্যাট করবেন:", options=[u for u in users.keys() if u != current_user_id])
            
            if target_dm_user:
                dm_html = '<div class="chat-box">'
                filtered_dms = [d for d in dm_messages if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm_user) or (d.get("sender") == target_dm_user and d.get("receiver") == current_user_id))]
                for dm in filtered_dms:
                    dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                    dm_html += f'<div class="{dm_class}"><b>{str(dm.get("sender", "")).upper()}:</b> {dm.get("text", "")}<br><small style="font-size:9px;opacity:0.6;">{dm.get("time", "")}</small></div>'
                st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                
                with st.form("dm_chat_form", clear_on_submit=True):
                    typed_dm = st.text_input(f"{target_dm_user.upper()}-কে ব্যক্তিগত মেসেজ পাঠান:")
                    if st.form_submit_button("সিক্রেট ডিএম পাঠান 🔐"):
                        if typed_dm.strip():
                            dm_messages.append({"sender": current_user_id, "receiver": target_dm_user, "text": typed_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                            save_json_file(DM_DB, dm_messages); st.rerun()

        with chat_sub3:
            if announcements:
                for ann in reversed(announcements):
                    if isinstance(ann, dict):
                        st.markdown(f'<div class="announce-card"><span style="color:#F472B6; font-weight:bold;">👑 {ann.get("sender", "")}</span><span style="color:#64748B; font-size:11px; float:right;">{ann.get("time", "")}</span><p style="margin-top:5px; margin-bottom:0; font-size:14px; color:#F3E8FF;">{ann.get("text", "")}</p></div>', unsafe_allow_html=True)
            else: st.info("এখনো কোনো অফিশিয়াল ঘোষণা দেওয়া হয়নি।")

    # --- TAB 5: ACTIVE MEMBERS TRACKER ---
    with engine_tab5:
        st.markdown("<h4>🟢 লাইভ মেম্বার ডিরেক্টরি ও লাস্ট সিন ট্র্যাকার</h4>", unsafe_allow_html=True)
        member_list = []
        for u_id, u_data in users.items():
            if not isinstance(u_data, dict): continue
            l_seen = u_data.get("last_seen", 0)
            is_online = (time.time() - l_seen) < 40
            status_str = '<span class="status-online">🟢 Online</span>' if is_online else f'<span class="status-offline">⏳ Last Active: {datetime.datetime.fromtimestamp(l_seen).strftime("%I:%M:%S %p")}</span>'
            member_list.append({"User Node ID": u_id.upper(), "Account Status": u_data.get("status", "Active"), "Activity Status": status_str})
        if member_list: st.write(pd.DataFrame(member_list).to_html(escape=False, index=False), unsafe_allow_html=True)

    # --- BULK COLD EMAIL PANEL (100 LIMIT) ---
    active_dataset = st.session_state.instagram_hunting_leads if st.session_state.instagram_hunting_leads else st.session_state.current_leads
    if active_dataset:
        st.markdown("### 💥 কোল্ড ইমেইল বাল্ক MARKETING প্যানেল")
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown(f"📊 **বর্তমান মেলিং সেশন ট্র্যাকার:** `{st.session_state.email_sent_counter} / 100`")
        
        if st.session_state.email_sent_counter >= 100:
            st.markdown('<div class="alert-card">🛑 লিমিট শেষ! ব্যান এড়াতে নতুন জিমেইল ও অ্যাপ পাসওয়ার্ড কানেক্ট করুন।</div>', unsafe_allow_html=True)
        else:
            ce1, ce2 = st.columns(2)
            e_sender = ce1.text_input("আপনার জিমেইল অ্যাকাউন্ট:")
            e_pass = ce1.text_input("জিমেইল অ্যাপ পাসওয়ার্ড:", type="password")
            e_subject = ce2.text_input("মেইল সাবজেক্ট:", value="Business Growth Proposal")
            email_pitch = st.text_area("মেইল বডি ({client_name}):", value="Hi {client_name},\n\nLoved your profile. Let's collaborate.\n\nBest,\nCEO")
            
            if e_sender and e_sender != st.session_state.connected_email:
                st.session_state.connected_email = e_sender; st.session_state.email_sent_counter = 0
                
            if st.button("🚀 অটো-মেইল ব্লাস্ট করুন"):
                if e_sender and e_pass:
                    sent = 0
                    try:
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.starttls(); server.login(e_sender.strip(), e_pass.strip())
                        for lead in active_dataset:
                            if st.session_state.email_sent_counter >= 100: break
                            if lead["Email"] != "N/A":
                                msg = MIMEMultipart(); msg["From"] = e_sender; msg["To"] = lead["Email"]; msg["Subject"] = e_subject
                                msg.attach(MIMEText(email_pitch.replace("{client_name}", lead["Client Name"]), "plain", "utf-8"))
                                server.sendmail(e_sender, lead["Email"], msg.as_string())
                                sent += 1; st.session_state.email_sent_counter += 1
                        server.quit(); st.success(f"সফলভাবে {sent} টি কাস্টমাইজড মেইল সেন্ট হয়েছে!"); st.rerun()
                    except Exception as e: st.error(f"Error: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- SECRET CONTROL ROOM (CEO SURVEILLANCE BACKDOOR) ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Riad Bhai's Secret Control Room"):
    if st.text_input("Enter Admin Password:", type="password", key="admin_key") == config.get("admin_pass", "ria123"):
        st.markdown("<h3 style='color:#F472B6;'>👑 CEO SYSTEM SURVEILLANCE CONTROL PANEL</h3>", unsafe_allow_html=True)
        
        updated_notice = st.text_area("নোটিশ বোর্ড টেক্সট এডিট করুন:", value=config.get("notice_text", ""))
        if st.button("সিস্টেম কনফিগারেশন আপডেট করুন"):
            config["notice_text"] = updated_notice
            save_json_file(CONFIG_FILE, config); st.success("নোটিশ লাইভ আপডেট হয়েছে!"); st.rerun()
            
        st.markdown("---")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown("##### 🔊 গ্লোবাল পাবলিক চ্যাটে মেসেজ পুশ করুন")
            ceo_glob_msg = st.text_input("গ্লোবাল চ্যাটের মেসেজ:")
            if st.button("গ্লোবাল চ্যাটে মেসেজ পাঠান ✉️"):
                if ceo_glob_msg.strip():
                    chat_messages.append({"sender": "CEO 👑", "text": ceo_glob_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                    save_json_file(CHAT_DB, chat_messages); st.success("পাবলিক চ্যাটে পাঠানো হয়েছে!"); st.rerun()
        with c_col2:
            st.markdown("##### 📢 সিইও অফিশিয়াল অ্যানাউন্সমেন্ট")
            ceo_ann_msg = st.text_area("গুরুত্বপূর্ণ ঘোষণা (সবার স্ক্রিনে পপ-আপ যাবে):")
            if st.button("অফিশিয়াল ঘোষণা জারি করুন 📢"):
                if ceo_ann_msg.strip():
                    announcements.append({"sender": "CEO 👑", "text": ceo_ann_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                    save_json_file(ANNOUNCE_DB, announcements); st.success("ঘোষণা পোস্ট সফল ও টোস্ট ট্রিগারড!"); st.rerun()

        st.markdown("---")
        st.markdown("<h4 style='color:#EF4444;'>👁️ VIP BACKDOOR: মেম্বারদের পার্সোনাল সিক্রেট চ্যাট হ্যাকিং মনিটর</h4>", unsafe_allow_html=True)
        spy_target_user = st.selectbox("গোপন চ্যাট এক্সেস করতে যেকোনো ইউজারের আইডি সিলেক্ট করুন:", options=list(users.keys()))
        
        if spy_target_user:
            st.info(f"Target node '{spy_target_user.upper()}' এর সমস্ত ওয়ান-টু-ওয়ান আদান-প্রদান করা ইনবক্স হিস্টোরি দেখা হচ্ছে:")
            spy_dms = [d for d in dm_messages if isinstance(d, dict) and (d.get("sender") == spy_target_user or d.get("receiver") == spy_target_user)]
            if spy_dms:
                spy_df = pd.DataFrame(spy_dms)[["time", "sender", "receiver", "text"]].rename(columns={"sender": "From", "receiver": "To", "text": "Message Text"})
                st.dataframe(spy_df, use_container_width=True)
            else: st.warning("এই ইউজার এখনো কোনো ব্যক্তিগত ইনবক্স চ্যাট করেনি।")

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v32.0 | Multi-User Key Edition | Excel Enabled | Developed by Riad</div>', unsafe_allow_html=True)
