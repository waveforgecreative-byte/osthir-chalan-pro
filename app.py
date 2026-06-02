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
import random
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- MULTI-USER SECURE STORAGE LAYER ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
HISTORY_DB = "users_history_memory.json"
CHAT_DB = "system_chat_memory.json"
DM_DB = "system_dm_memory.json"
COMPLAINT_DB = "system_complaints.json"
ASAMI_DB = "system_asami_board.json"

DEFAULT_CONFIG = {
    "master_pin": "69", 
    "admin_pass": "reyadh123", 
    "notice_text": "📢 ২-ডিজিটের গোপন পিন ব্যবহার করে ড্যাশবোর্ড আনলক করুন।"
}

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f: return json.load(f)
        except: return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- INITIALIZE DATABASE CACHE ---
if "users_cache" not in st.session_state: st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state: st.session_state.config_cache = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
if "history_cache" not in st.session_state: st.session_state.history_cache = load_json_file(HISTORY_DB, [])
if "chat_cache" not in st.session_state: st.session_state.chat_cache = load_json_file(CHAT_DB, [])
if "dm_cache" not in st.session_state: st.session_state.dm_cache = load_json_file(DM_DB, [])
if "complaint_cache" not in st.session_state: st.session_state.complaint_cache = load_json_file(COMPLAINT_DB, [])
if "asami_cache" not in st.session_state: st.session_state.asami_cache = load_json_file(ASAMI_DB, {})

users = st.session_state.users_cache
config = st.session_state.config_cache
history_logs = st.session_state.history_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
complaints = st.session_state.complaint_cache
asami_list = st.session_state.asami_cache

st.set_page_config(page_title="অস্থির চালান PRO v45.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; font-family: 'Hind Siliguri', sans-serif; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; font-family: 'Hind Siliguri', sans-serif; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    
    .asami-card { background: linear-gradient(135deg, #450A0A, #7F1D1D); border: 2px dashed #EF4444; padding: 15px; border-radius: 8px; color: #FCA5A5; font-family: 'Hind Siliguri', sans-serif; margin-bottom: 10px; box-shadow: 0 0 10px rgba(239,68,68,0.3); }
    .lock-box { background: linear-gradient(90deg, #450A0A, #1A0505); border-left: 6px solid #EF4444; padding: 20px; border-radius: 8px; color: #FCA5A5; font-weight: bold; margin-bottom: 20px; font-family: 'Hind Siliguri', sans-serif; }
    
    .chat-box { height: 420px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    .msg-ceo { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border: 2px solid #F472B6; font-weight: bold; width: fit-content; text-shadow: 0 0 5px #F472B6; }
    .msg-ceo-self { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; border: 2px solid #F472B6; font-weight: bold; width: fit-content; text-shadow: 0 0 5px #F472B6; }
    
    .vcall-btn-group { background: linear-gradient(90deg, #00FF66, #007A3D) !important; color: black !important; font-weight: bold !important; border-radius: 8px !important; text-align: center; padding: 10px; text-decoration: none; display: inline-block; margin-bottom: 15px; width: 100%; box-shadow: 0 0 10px rgba(0,255,102,0.4); }
    .vcall-btn-private { background: linear-gradient(90deg, #FF007F, #7928CA) !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; text-align: center; padding: 10px; text-decoration: none; display: inline-block; margin-bottom: 15px; width: 100%; box-shadow: 0 0 10px rgba(255,0,127,0.4); }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "is_ceo" not in st.session_state: st.session_state.is_ceo = False
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "insta_query_saved" not in st.session_state: st.session_state.insta_query_saved = ""
if "active_dm_user" not in st.session_state: st.session_state.active_dm_user = None

# --- ASAMI LOCK CHECKER ---
def check_user_lock(u_id):
    if u_id == "CEO 👑" or not u_id: return False, ""
    if u_id in asami_list:
        lock_until_ts = asami_list[u_id].get("lock_until_ts", 0)
        current_ts = time.time()
        if current_ts < lock_until_ts:
            rem_seconds = lock_until_ts - current_ts
            hours = int(rem_seconds // 3600)
            minutes = int((rem_seconds % 3600) // 60)
            if hours > 0: return True, f"{hours} ঘণ্টা {minutes} মিনিট"
            else: return True, f"{minutes} মিনিট"
        else:
            del asami_list[u_id]
            save_json_file(ASAMI_DB, asami_list)
    return False, ""

def get_badge(u_id):
    badge_str = ""
    if u_id == "CEO 👑": return " [CEO 👑]"
    is_locked, _ = check_user_lock(u_id)
    if is_locked: badge_str += f" <span style='color:#EF4444; font-weight:bold;'>[🚨 দাগী আসামি - জেলে বন্দী]</span>"
    elif u_id in asami_list: badge_str += f" <span style='color:#FCA5A5; font-weight:bold;'>[🚨 দাগী আসামি]</span>"
        
    u_data = users.get(u_id, {})
    badge = u_data.get("badge", "None")
    if badge == "Blue Tick 🔵": badge_str += " 🔵"
    elif badge == "Always Active 🔥": badge_str += " 🔥"
    elif badge == "Low Active 💤": badge_str += " 💤"
    return badge_str

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v45.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice-board">{config.get("notice_text", "")}</div>', unsafe_allow_html=True)
    login_mode = st.radio("🔑 লগইন টাইপ সিলেক্ট করুন:", ["👤 সাধারণ মেম্বার পোর্টাল", "👑 সিইও সিকিউর পোর্টাল"], horizontal=True)
    
    if login_mode == "👑 সিইও সিকিউর পোর্টাল":
        st.markdown("### 🔒 CEO Core Encrypted Login")
        ceo_pass = st.text_input("সিইও মাস্টার পাসওয়ার্ড দিন:", type="password")
        if st.button("মাস্টার ড্যাশবোর্ড বুট করুন ⚡"):
            if ceo_pass == config.get("admin_pass", "reyadh123"):
                st.session_state.is_ceo = True; st.session_state.logged_in_user = "CEO 👑"; st.rerun()
            else: st.error("❌ ভুল পাসওয়ার্ড!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📝 নতুন অ্যাকাউন্ট খুলুন")
            reg_id = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_uid")
            reg_name = st.text_input("আপনার সম্পূর্ণ নাম (Full Name):", key="reg_fullname")
            if st.button("অ্যাকাউন্ট তৈরি করুন ✅"):
                if reg_id.strip() and reg_name.strip() and reg_id.strip() not in users:
                    users[reg_id.strip()] = {"name": reg_name.strip(), "badge": "None", "user_api_key": "", "last_seen": time.time()}
                    save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট ডান!")
        with col2:
            st.markdown("### 🔑 ড্যাশবোর্ড লগইন")
            login_id = st.text_input("ইউজার আইডি (User ID):", key="login_uid")
            input_pin = st.text_input("২-ডিজিট পিন:", type="password", key="login_pin", max_chars=2)
            if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
                if login_id in users and str(input_pin).strip() == str(config.get("master_pin", "69")).strip():
                    users[login_id]["last_seen"] = time.time(); save_json_file(USER_DB, users)
                    st.session_state.logged_in_user = login_id; st.session_state.is_ceo = False; st.rerun()
                else: st.error("❌ ভুল পিন বা আইডি।")
else:
    current_user_id = st.session_state.logged_in_user
    is_ceo_active = st.session_state.is_ceo
    user_real_name = "MD Reyadh" if is_ceo_active else users[current_user_id].get("name", current_user_id)
    
    if is_ceo_active: st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    is_current_user_locked, remaining_lock_time = check_user_lock(current_user_id)

    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5 = st.tabs([
        "📍 Google Maps Scraper & Mail Engine", 
        "📸 Instagram AI Global Hunter", 
        "💬 Cyber Messenger & Media Room",
        "🚨 পাবলিক আসামি থানা বোর্ড",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1: GOOGLE MAPS ---
    with engine_tab1:
        st.subheader("📍 Google Maps Live Scraping & Smart Variable Mailer")
        if is_current_user_locked:
            st.markdown(f"""
            <div class="lock-box">
                ❌ অ্যাক্সেস ডিনাইড! সিইও রিয়াদ ভাই আপনার এই ইঞ্জিনটি লক করেছেন। <br>
                ⚖️ অপরাধের কারণ: {asami_list[current_user_id].get('crime')}<br>
                ⏳ আপনার সাজার মেয়াদ আরও {remaining_lock_time} বাকি আছে! চ্যাট রুমে গিয়ে মাফি চান। 🫡
            </div>
            """, unsafe_allow_html=True)
        else:
            saved_key = "" if is_ceo_active else users[current_user_id].get("user_api_key", "")
            g_api_key = st.text_input("🔑 SerpApi Key:", type="password", value=saved_key)
            sc_col1, sc_col2 = st.columns(2)
            search_query = sc_col1.text_input("গুগল ম্যাপস লাইভ সার্চ কিওয়ার্ড:")
            max_results = sc_col2.number_input("সর্বোচ্চ লিড সংখ্যা:", min_value=1, max_value=50, value=5)
            
            if st.button("গুগল ম্যাপস লাইভ স্ক্র্যাপার রান করুন ⚡") and search_query.strip() and g_api_key:
                with st.spinner("ডাটা স্ক্র্যাপ হচ্ছে..."):
                    res = requests.get("https://serpapi.com/search.json", params={"engine": "google_maps", "q": search_query.strip(), "api_key": g_api_key.strip(), "num": int(max_results)})
                    if res.status_code == 200:
                        local_results = res.json().get("local_results", [])
                        st.session_state.current_leads = []
                        for item in local_results:
                            title = item.get("title", "Business")
                            website = item.get("website", "None")
                            clean_domain = website.replace("https://", "").replace("http://", "").replace("www.", "") if website else ""
                            raw_domain = clean_domain.split("/")[0] if clean_domain else ""
                            generated_email = f"info@{raw_domain}" if raw_domain else "None"
                            st.session_state.current_leads.append({"Name": title, "Email": generated_email, "Website": website, "Phone": item.get("phone", "None")})
                        st.success(f"✅ সফলভাবে {len(st.session_state.current_leads)}টি লিড লোড হয়েছে!")
            
            if st.session_state.current_leads:
                st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)

    # --- TAB 2: INSTAGRAM HUNTER ---
    with engine_tab2:
        st.markdown("<h2 style='color:#00FF66;'>📸 ইনস্টাগ্রাম AI গ্লোবাল হান্টার</h2>", unsafe_allow_html=True)
        target_category = st.selectbox("🎯 ক্লায়েন্ট ক্যাটাগরি:", options=["Real Estate Agents", "Fitness Coaches", "Custom"])
        inst_query = st.text_input("🔍 কাস্টম ক্যাটাগরি:") if target_category == "Custom" else target_category
        if st.button("🚀 গ্লোবাল হান্টিং রাডার অ্যাক্টিভেট করুন") and inst_query.strip(): st.session_state.insta_query_saved = inst_query.strip()
        if st.session_state.insta_query_saved:
            final_google_query = f'site:instagram.com "{st.session_state.insta_query_saved}"'
            st.markdown(f'<a href="https://www.google.com/search?q={urllib.parse.quote(final_google_query)}" target="_blank"><button style="background-color:#4285F4; color:white; padding:12px; border:none; border-radius:8px; width:100%;">🎯 গুগল এক্স-রে ফিল্টার ওপেন করুন</button></a>', unsafe_allow_html=True)

    # --- TAB 3: CYBER MESSENGER & MEDIA ROOM (১:১ এবং গ্রুপ কল ফিচার আলাদা) ---
    with engine_tab3:
        st.markdown("### 🔊 সাইবার মাল্টিমিডিয়া চ্যাট ও ভয়েস/ভিডিও মেকানিজম")
        
        chat_sub1, chat_sub2 = st.tabs(["🔊 Global Public Chat Room (গ্রুপ চ্যাট)", "🔒 Secret 1:1 Personal DM Portal (গোপন ইনবক্স)"])
        
        # --- গ্লোবাল গ্রুপ চ্যাট সাব-ট্যাব ---
        with chat_sub1:
            # 🎥 ১-ক্লিক গ্লোবাল গ্রুপ ভিডিও কল লিংক জেনারেটর (সবাই একসাথে আড্ডা দেওয়ার জন্য)
            st.markdown("#### 👥 গ্লোবাল গ্রুপ ভিডিও কল (সবাই একসাথে যোগ দিন)")
            group_room_url = "https://meet.jit.si/reyadh-osthir-chalawn-global-group"
            st.markdown(f'<a href="{group_room_url}" target="_blank" class="vcall-btn-group">🔊 গ্রুপ ভিডিও কল রুমে ঢুকুন (সবাই একসাথে ক্যাচাল পাড়ুন) 🎥🔊</a>', unsafe_allow_html=True)
            
            col_chat, col_members = st.columns([4, 1.5])
            with col_chat:
                chat_html = '<div class="chat-box">'
                for msg in chat_messages:
                    if not isinstance(msg, dict): continue
                    sender_id = msg.get("sender")
                    
                    if sender_id == "CEO 👑":
                        sender_display = "MD Reyadh [CEO 👑]"
                        msg_class = "msg-ceo-self" if is_ceo_active else "msg-ceo"
                    else:
                        sender_display = users.get(sender_id, {}).get("name", sender_id) + get_badge(sender_id)
                        msg_class = "msg-outgoing" if sender_id == current_user_id else "msg-incoming"
                    
                    chat_html += f'<div class="{msg_class}"><b>{sender_display}:</b> '
                    
                    if msg.get("type") == "voice":
                        chat_html += f'🎤 <span style="color:#FF007F; font-weight:bold;">ভয়েস মেসেজ পাঠিয়েছেন!</span>'
                        st.markdown(chat_html, unsafe_allow_html=True)
                        try:
                            audio_bytes = base64.b64decode(msg.get("audio_base64", ""))
                            st.audio(audio_bytes, format="audio/mp3")
                        except: st.write("⚠️ ভয়েস লোড হতে ব্যর্থ।")
                        chat_html = f'<div style="font-size:9px;opacity:0.5;margin-bottom:8px;">{msg.get("time","")}</div>'
                    else:
                        chat_html += f'{msg.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{msg.get("time","")}</small></div>'
                
                if chat_html != f'<div style="font-size:9px;opacity:0.5;margin-bottom:8px;">':
                    st.markdown(chat_html + '</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                c_in1, c_in2 = st.columns([3, 2])
                with c_in1:
                    with st.form("pub_text_v45", clear_on_submit=True):
                        t_msg = st.text_input("📝 টেক্সট মেসেজ লিখুন:")
                        if st.form_submit_button("পাঠান ✉️") and t_msg.strip():
                            sender_identity = "CEO 👑" if is_ceo_active else current_user_id
                            chat_messages.append({"sender": sender_identity, "type": "text", "text": t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                            save_json_file(CHAT_DB, chat_messages); st.rerun()
                with c_in2:
                    voice_file = st.file_uploader("ভয়েস ফাইল আপলোড করুন:", type=["mp3", "wav", "m4a"], key="global_voice")
                    if voice_file is not None and st.button("🎤 ভয়েস সেন্ড করুন"):
                        base64_audio = base64.b64encode(voice_file.read()).decode("utf-8")
                        sender_identity = "CEO 👑" if is_ceo_active else current_user_id
                        chat_messages.append({"sender": sender_identity, "type": "voice", "audio_base64": base64_audio, "time": datetime.datetime.now().strftime("%I:%M %p")})
                        save_json_file(CHAT_DB, chat_messages); st.success("✅ সেন্ট!"); time.sleep(0.5); st.rerun()
            
            with col_members:
                st.markdown("### 👥 একটিভ মেম্বার্স")
                for u_id, u_data in users.items():
                    if u_id != current_user_id:
                        asami_tag = " 🚨" if u_id in asami_list else ""
                        if st.button(f"💬 {u_data.get('name')}{asami_tag}", key=f"quick_dm_{u_id}"):
                            st.session_state.active_dm_user = u_id; st.rerun()
        
        # --- ওয়ান-টু-ওয়ান (১:১) সিক্রেট ডিএম সাব-ট্যাব ---
        with chat_sub2:
            st.markdown("#### 🔒 ওয়ান-টু-ওয়ান সিক্রেট ইনবক্স ও প্রাইভেট ট্রাইব্যুনাল")
            all_users_list = [u for u in users.keys() if u != current_user_id]
            default_index = all_users_list.index(st.session_state.active_dm_user) if st.session_state.active_dm_user in all_users_list else 0
            
            if all_users_list:
                target_dm = st.selectbox("যার সাথে ওয়ান-টু-ওয়ান চ্যাট/কল করবেন তাকে সিলেক্ট করুন:", options=all_users_list, index=default_index)
                if target_dm:
                    st.session_state.active_dm_user = target_dm
                    
                    # 🔒 ডাইনামিক ১:১ প্রাইভেট ভিডিও কল লিংক মেকার (শুধুমাত্র এই দুজন ঢুকতে পারবে)
                    # ইউজারনেমগুলোকে সর্ট করে হ্যাশ রুম বানানো যাতে রিয়াদ->আসামি অথবা আসামি->রিয়াদ একই রুমে ল্যান্ড করে
                    sorted_pair = sorted([str(current_user_id), str(target_dm)])
                    private_room_id = f"reyadh-private-1to1-{sorted_pair[0]}-{sorted_pair[1]}"
                    private_call_url = f"https://meet.jit.si/{private_room_id}"
                    
                    target_display_name = "আসামি" if target_dm in asami_list else users.get(target_dm, {}).get("name", target_dm)
                    st.markdown(f'<a href="{private_call_url}" target="_blank" class="vcall-btn-private">🔒 {target_display_name}-এর সাথে ১:১ প্রাইভেট ভিডিও কল (একলা সাইজ করুন) 🔒🎥</a>', unsafe_allow_html=True)
                    
                    dm_html = '<div class="chat-box">'
                    filtered_dms = [d for d in dm_messages if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm) or (d.get("sender") == target_dm and d.get("receiver") == current_user_id))]
                    
                    for dm in filtered_dms:
                        dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else users.get(dm.get("sender"), {}).get("name", dm.get("sender"))
                        dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                        
                        dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> '
                        if dm.get("type") == "voice":
                            dm_html += f'🎤 <span style="color:#FF007F; font-weight:bold;">সিক্রেট ভয়েস মেসেজ!</span>'
                            st.markdown(dm_html, unsafe_allow_html=True)
                            try:
                                audio_bytes = base64.b64decode(dm.get("audio_base64", ""))
                                st.audio(audio_bytes, format="audio/mp3")
                            except: pass
                            dm_html = f'<div style="font-size:9px;opacity:0.5;margin-bottom:8px;">{dm.get("time","")}</div>'
                        else:
                            dm_html += f'{dm.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{dm.get("time","")}</small></div>'
                    
                    if dm_html != f'<div style="font-size:9px;opacity:0.5;margin-bottom:8px;">':
                        st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    cdm1, cdm2 = st.columns([3, 2])
                    with cdm1:
                        with st.form("dm_text_v45", clear_on_submit=True):
                            t_dm = st.text_input("গোপন মেসেজ লিখুন:")
                            if st.form_submit_button("ডিএম পাঠান 🔐") and t_dm.strip():
                                sender_identity = "CEO 👑" if is_ceo_active else current_user_id
                                dm_messages.append({"sender": sender_identity, "receiver": target_dm, "type": "text", "text": t_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                                save_json_file(DM_DB, dm_messages); st.rerun()
                    with cdm2:
                        dm_voice_file = st.file_uploader("গোপন ভয়েস ফাইল:", type=["mp3", "wav", "m4a"], key="dm_voice")
                        if dm_voice_file is not None and st.button("🔒 গোপন ভয়েস পাঠান"):
                            base64_audio = base64.b64encode(dm_voice_file.read()).decode("utf-8")
                            sender_identity = "CEO 👑" if is_ceo_active else current_user_id
                            dm_messages.append({"sender": sender_identity, "receiver": target_dm, "type": "voice", "audio_base64": base64_audio, "time": datetime.datetime.now().strftime("%I:%M %p")})
                            save_json_file(DM_DB, dm_messages); st.success("✅ গোপন ভয়েস সেন্ট!"); time.sleep(0.5); st.rerun()
            else:
                st.info("কোনো অতিরিক্ত মেম্বার এখনো রেজিস্টার্ড নেই।")

    # --- TAB 4: PUBLIC ASAMI BOARD ---
    with engine_tab4:
        st.markdown("<h2 style='color:#EF4444;'>🚨 অস্থির চালান - সাইবার থানা আসামি বোর্ড 🚓</h2>", unsafe_allow_html=True)
        if asami_list:
            for a_id, a_info in list(asami_list.items()):
                is_locked, _ = check_user_lock(a_id)
                a_name = users.get(a_id, {}).get("name", a_id)
                st.markdown(f"""
                <div class="asami-card">
                    <h4>👤 আসামি: {a_name} (ID: {a_id})</h4>
                    <p style="margin:2px 0;">❌ <b>অপরাধের বিবরণ:</b> <span style="color:#FFF; font-weight:bold;">{a_info.get('crime')}</span></p>
                    <p style="margin:2px 0; color:#FCA5A5;">⏳ <b>সাজার মেয়াদ:</b> <span style="color:#FF0000; font-weight:bold;">{a_info.get('duration')} দিন</span></p>
                    <p style="margin:2px 0; font-size:12px;">⚖️ <b>রায় ঘোষণা করেছেন:</b> {a_info.get('judge')} | ⏱️ {a_info.get('date')}</p>
                </div>
                """, unsafe_allow_html=True)
        else: st.info("🕊️ ড্যাশবোর্ডে এখন কোনো আসামি নেই!")

    # --- TAB 5: CEO SECRET CONTROL ROOM ---
    with engine_tab5:
        st.subheader("👑 Riad Bhai's Secret Control Room")
        if is_ceo_active:
            st.success("🔓 ফুল সিইও কন্ট্রোল অ্যাক্টিভেটেড!")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                st.markdown("#### ⚖️ নতুন আসামি গ্রেপ্তার ও কাস্টম লক সেট করুন:")
                all_users_avail = list(users.keys())
                if all_users_avail:
                    target_suspect = st.selectbox("কাকে আসামি বানাবেন?", options=all_users_avail, key="suspect_box_v45")
                    crime_note = st.text_input("অপরাধ বা ট্রোলের কারণ লিখুন:")
                    lock_days = st.number_input("🔒 কতদিনের জন্য স্ক্র্যাপার লক করবেন? (Days):", min_value=1, max_value=30, value=2)
                    
                    if st.button("🔨 রায় ঘোষণা করুন", use_container_width=True):
                        if crime_note.strip():
                            seconds_to_add = int(lock_days) * 86400
                            future_ts = time.time() + seconds_to_add
                            asami_list[target_suspect] = {"crime": crime_note.strip(), "duration": str(lock_days), "lock_until_ts": future_ts, "judge": "MD Reyadh [CEO 👑]", "date": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")}
                            save_json_file(ASAMI_DB, asami_list); st.success("🚓 সফলভাবে লকআপে চালান হয়েছে!"); time.sleep(0.5); st.rerun()
            with c_col2:
                st.markdown("#### 🕊️ আসামি খালাস করুন:")
                if asami_list:
                    free_suspect = st.selectbox("কাকে মুক্তি দিবেন?", options=list(asami_list.keys()))
                    if st.button("🔓 জেল থেকে মুক্তি দিন", use_container_width=True):
                        if free_suspect in asami_list: del asami_list[free_suspect]; save_json_file(ASAMI_DB, asami_list); st.success("মুক্ত ও আনলক করা হয়েছে!"); time.sleep(0.5); st.rerun()
            st.markdown("---")
            new_notice = st.text_area("মেইন পেজের নোটিশ:", value=config.get("notice_text", ""))
            new_pin = st.text_input("২-ডিজিট মাস্টার পিন:", value=config.get("master_pin", "69"), max_chars=2)
            if st.button("কনফিগারেশন সেভ করুন 💾"):
                config["notice_text"] = new_notice; config["master_pin"] = new_pin; save_json_file(CONFIG_FILE, config); st.success("✅ ডান!")
        else: st.error("🔒 এই সেকশনটি শুধুমাত্র মেইন সিইও পোর্টাল দিয়ে এক্সেস করা যাবে।")

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v45.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
