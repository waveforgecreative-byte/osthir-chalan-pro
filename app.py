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
ANNOUNCE_DB = "system_announcements.json"
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

st.set_page_config(page_title="অস্থির চালান PRO v39.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; font-family: 'Hind Siliguri', sans-serif; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; font-family: 'Hind Siliguri', sans-serif; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    
    /* Asami Board Styling */
    .asami-card { background: linear-gradient(135deg, #450A0A, #7F1D1D); border: 2px dashed #EF4444; padding: 12px; border-radius: 8px; color: #FCA5A5; font-family: 'Hind Siliguri', sans-serif; margin-bottom: 8px; box-shadow: 0 0 10px rgba(239,68,68,0.3); }
    
    .chat-box { height: 380px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    .msg-ceo { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border: 2px solid #F472B6; font-weight: bold; width: fit-content; text-shadow: 0 0 5px #F472B6; }
    .msg-ceo-self { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; border: 2px solid #F472B6; font-weight: bold; width: fit-content; text-shadow: 0 0 5px #F472B6; }
    
    .complaint-card { background: #1E1B4B; border-left: 4px solid #EF4444; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #EEF2F6; }
    .reply-card { background: #064E3B; border-left: 4px solid #10B981; padding: 8px 12px; border-radius: 6px; margin-top: 5px; color: #D1FAE5; font-size: 13px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "is_ceo" not in st.session_state: st.session_state.is_ceo = False
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "insta_query_saved" not in st.session_state: st.session_state.insta_query_saved = ""
if "active_dm_user" not in st.session_state: st.session_state.active_dm_user = None

def get_badge(u_id):
    badge_str = ""
    if u_id == "CEO 👑": return " [CEO 👑]"
    
    # আসামি চেক (Funny Addition)
    if u_id in asami_list:
        badge_str += f" <span style='color:#EF4444; font-weight:bold;'>[🚨 আসামি: {asami_list[u_id]['crime']}]</span>"
        
    u_data = users.get(u_id, {})
    badge = u_data.get("badge", "None")
    if badge == "Blue Tick 🔵": badge_str += " 🔵"
    elif badge == "Always Active 🔥": badge_str += " 🔥"
    elif badge == "Low Active 💤": badge_str += " 💤"
    return badge_str

# --- LOGIN / REGISTRATION GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v39.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice-board">{config.get("notice_text", "")}</div>', unsafe_allow_html=True)
    
    login_mode = st.radio("🔑 লগইন টাইপ সিলেক্ট করুন:", ["👤 সাধারণ মেম্বার পোর্টাল", "👑 সিইও সিকিউর পোর্টাল"], horizontal=True)
    
    if login_mode == "👑 সিইও সিকিউর পোর্টাল":
        st.markdown("### 🔒 CEO Core Encrypted Login")
        ceo_pass = st.text_input("সিইও মাস্টার পাসওয়ার্ড দিন:", type="password")
        if st.button("মাস্টার ড্যাশবোর্ড বুট করুন ⚡"):
            if ceo_pass == config.get("admin_pass", "reyadh123"):
                st.session_state.is_ceo = True
                st.session_state.logged_in_user = "CEO 👑"
                st.rerun()
            else: st.error("❌ ভুল মাস্টার পাসওয়ার্ড!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📝 নতুন অ্যাকাউন্ট খুলুন")
            reg_id = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_uid")
            reg_name = st.text_input("আপনার সম্পূর্ণ নাম (Full Name):", key="reg_fullname")
            if st.button("অ্যাকাউন্ট তৈরি করুন ✅"):
                if reg_id.strip() and reg_name.strip() and reg_id.strip() not in users:
                    users[reg_id.strip()] = {"name": reg_name.strip(), "badge": "None", "is_moderator": False, "user_api_key": "", "last_seen": time.time()}
                    save_json_file(USER_DB, users); st.success("✅ অ্যাক্টিভেটেড! লগইন করুন।")
                else: st.error("❌ ঘর পূরণ করুন বা আইডি অলরেডি আছে।")
        with col2:
            st.markdown("### 🔑 ড্যাশবোর্ড লগইন")
            login_id = st.text_input("ইউজার আইডি (User ID):", key="login_uid")
            input_pin = st.text_input("২-ডিজিট পিন:", type="password", key="login_pin", max_chars=2)
            if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
                if login_id in users and str(input_pin).strip() == str(config.get("master_pin", "69")).strip():
                    users[login_id]["last_seen"] = time.time(); save_json_file(USER_DB, users)
                    st.session_state.logged_in_user = login_id; st.session_state.is_ceo = False; st.rerun()
                else: st.error("❌ ভুল শংসাপত্র।")
else:
    current_user_id = st.session_state.logged_in_user
    is_ceo_active = st.session_state.is_ceo
    user_real_name = "MD Reyadh" if is_ceo_active else users[current_user_id].get("name", current_user_id)
    
    if is_ceo_active:
        st.markdown(f'<div class="welcome-banner">👑 সিইও কন্ট্রোল একটিভ! চ্যাটে সরাসরি "CEO 👑" মোড অন, পাশে স্পেশাল গ্লোয়িং ইফেক্ট থাকবে।</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন আজকে অস্থিরভাবে ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): 
        st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5 = st.tabs([
        "📍 Google Maps Scraper & Mail Engine", 
        "📸 Instagram AI Global Hunter", 
        "💬 Cyber Messenger & Quick DM",
        "🚨 পাবলিক আসামি থানা বোর্ড",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1 & 2 (বাকি ফিচারগুলো স্ট্যাবল রাখা হয়েছে) ---
    with engine_tab1:
        st.subheader("📍 Google Maps Live Scraping & Smart Variable Mailer")
        saved_key = "" if is_ceo_active else users[current_user_id].get("user_api_key", "")
        g_api_key = st.text_input("🔑 SerpApi Key:", type="password", value=saved_key)
        search_query = st.text_input("গুগল ম্যাপস লাইভ সার্চ কিওয়ার্ড:")
        if st.button("গুগল ম্যাপস লাইভ স্ক্র্যাপার রান করুন ⚡") and search_query.strip() and g_api_key:
            with st.spinner("ডাটা স্ক্র্যাপ হচ্ছে..."):
                res = requests.get("https://serpapi.com/search.json", params={"engine": "google_maps", "q": search_query.strip(), "api_key": g_api_key.strip(), "num": 5})
                if res.status_code == 200:
                    local_results = res.json().get("local_results", [])
                    st.session_state.current_leads = [{"Name": item.get("title", "Biz"), "Email": f"info@{item.get('website','').replace('https://','').replace('www.','').split('/')[0]}" if item.get('website') else "None", "Website": item.get("website", "None")} for item in local_results]
                    st.success("লিড লোড ডান!")
        if st.session_state.current_leads:
            st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)

    with engine_tab2:
        st.subheader("📸 ইনস্টাগ্রাম আনলিমিটেড AI গ্লোবাল হান্টার")
        inst_query = st.text_input("🔍 বায়ারের ক্যাটাগরি/নিশ লিখুন:", key="insta_q_v39")
        if st.button("🚀 রাডার অন করুন") and inst_query.strip():
            st.session_state.insta_query_saved = inst_query.strip()
        if st.session_state.insta_query_saved:
            encoded_q = urllib.parse.quote(f'site:instagram.com "{st.session_state.insta_query_saved}"')
            st.markdown(f'<a href="https://google.com/search?q={encoded_q}" target="_blank"><button style="background-color:#4285F4; color:white; padding:12px; border:none; border-radius:8px;">🎯 গুগল এক্স-রে ফিল্টার ওপেন করুন</button></a>', unsafe_allow_html=True)

    # --- TAB 3: CYBER MESSENGER & QUICK DM (DIRECT TRIGGER UPGRADED) ---
    with engine_tab3:
        chat_sub1, chat_sub2 = st.tabs(["🔊 Global Public Chat Room", "🔒 Secret 1:1 Personal DM Portal"])
        
        with chat_sub1:
            col_chat, col_members = st.columns([4, 1.5])
            
            with col_chat:
                chat_html = '<div class="chat-box">'
                for msg in chat_messages:
                    if not isinstance(msg, dict): continue
                    
                    if msg.get("sender") == "CEO 👑":
                        sender_display = "MD Reyadh [CEO 👑]"
                        msg_class = "msg-ceo-self" if is_ceo_active else "msg-ceo"
                    else:
                        sender_display = users.get(msg.get("sender"), {}).get("name", msg.get("sender")) + get_badge(msg.get("sender"))
                        msg_class = "msg-outgoing" if msg.get("sender") == current_user_id else "msg-incoming"
                    
                    chat_html += f'<div class="{msg_class}"><b>{sender_display}:</b> {msg.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{msg.get("time","")}</small></div>'
                st.markdown(chat_html + '</div>', unsafe_allow_html=True)
                
                with st.form("pub_chat_v39", clear_on_submit=True):
                    t_msg = st.text_input("মেসেজ লিখুন:")
                    if st.form_submit_button("পাঠান ✉️") and t_msg.strip():
                        sender_identity = "CEO 👑" if is_ceo_active else current_user_id
                        chat_messages.append({"sender": sender_identity, "text": t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                        save_json_file(CHAT_DB, chat_messages); st.rerun()
            
            with col_members:
                st.markdown("### 👥 একটিভ মেম্বার্স লিস্ট")
                st.caption("👉 সরাসরি ওয়ান-ক্লিক মেসেজ পাঠাতে নামের পাশের বাটনে চাপুন:")
                for u_id, u_data in users.items():
                    if u_id != current_user_id:
                        asami_tag = " 🚨" if u_id in asami_list else ""
                        if st.button(f"💬 {u_data.get('name')}{asami_tag} ({u_id})", key=f"quick_dm_{u_id}"):
                            st.session_state.active_dm_user = u_id
                            st.info(f"🔒 {u_data.get('name')} এর সিক্রেট ডিএম পোর্টাল লোড হয়েছে! পাশের ট্যাবে যান।")
        
        with chat_sub2:
            st.markdown("#### 🔒 ওয়ান-টু-ওয়ান সিক্রেট পার্সোনাল ইনবক্স")
            # কুইক চ্যাট ট্রিগার ইন্টিগ্রেশন
            default_index = 0
            all_users_list = [u for u in users.keys() if u != current_user_id]
            if st.session_state.active_dm_user in all_users_list:
                default_index = all_users_list.index(st.session_state.active_dm_user)
                
            target_dm = st.selectbox("মেম্বার সিলেক্ট করুন (বা বামের প্যানেল থেকে ডাইরেক্ট ক্লিক করে আসুন):", options=all_users_list, index=default_index)
            
            if target_dm:
                st.session_state.active_dm_user = target_dm
                dm_html = '<div class="chat-box">'
                filtered_dms = [d for d in dm_messages if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm) or (d.get("sender") == target_dm and d.get("receiver") == current_user_id))]
                for dm in filtered_dms:
                    dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else users.get(dm.get("sender"), {}).get("name", dm.get("sender"))
                    dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                    dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{dm.get("time","")}</small></div>'
                st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                
                with st.form("dm_form_v39", clear_on_submit=True):
                    t_dm = st.text_input("গোপন মেসেজ লিখুন:")
                    if st.form_submit_button("ডিএম পাঠান 🔐") and t_dm.strip():
                        sender_identity = "CEO 👑" if is_ceo_active else current_user_id
                        dm_messages.append({"sender": sender_identity, "receiver": target_dm, "text": t_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                        save_json_file(DM_DB, dm_messages); st.rerun()

    # --- TAB 4: 🚨 পাবলিক আসামি থানা বোর্ড (FUNNY CRIME BOARD) ---
    with engine_tab4:
        st.markdown("<h2 style='color:#EF4444; font-family:Hind Siliguri;'>🚨 অস্থির চালান - ডিজিটাল সাইবার থানা ও আসামি বোর্ড 🚓</h2>", unsafe_allow_html=True)
        st.write("সিইও রিয়াদ ভাই কর্তৃক দণ্ডপ্রাপ্ত এবং ট্রোলের শিকার আসামিদের তালিকা। এখানে নাম উঠলে চ্যাট বক্সে আপনার আইডি লাল হয়ে যাবে! 😂")
        st.write("---")
        
        if asami_list:
            for a_id, a_info in asami_list.items():
                a_name = users.get(a_id, {}).get("name", a_id)
                st.markdown(f"""
                <div class="asami-card">
                    <h4>👤 আসামি: {a_name} (ID: {a_id})</h4>
                    <p style="margin:2px 0;">❌ <b>অপরাধের বিবরণ:</b> <span style="color:#FEE2E2; font-weight:bold;">{a_info.get('crime')}</span></p>
                    <p style="margin:2px 0; font-size:12px; color:#FCA5A5;">⚖️ <b>রায় ঘোষণা করেছেন:</b> {a_info.get('judge', 'CEO 👑')} | ⏱️ {a_info.get('date')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🕊️ ড্যাশবোর্ডে এখন কোনো আসামি নেই! সবাই খুব ভালো মানুষের মতো ক্লায়েন্ট হান্ট করছে।")

    # --- TAB 5: CEO SECRET CONTROL ROOM (ASAMI MANAGEMENT INJECTED) ---
    with engine_tab5:
        st.subheader("👑 Riad Bhai's Secret Control Room")
        if is_ceo_active:
            st.success("🔓 ফুল সিইও কন্ট্রোল অ্যাক্টিভেটেড!")
            
            # আসামি ম্যানেজমেন্ট সেকশন (Funny Integration)
            st.markdown("### 🚨 আসামি লিস্ট কন্ট্রোল প্যানেল (Funny Court Room)")
            c_col1, c_col2 = st.columns(2)
            
            with c_col1:
                st.markdown("#### ⚖️ নতুন আসামি গ্রেপ্তার করুন:")
                target_suspect = st.selectbox("কাকে আসামি বানাবেন?", options=list(users.keys()), key="suspect_box")
                crime_note = st.text_input("অপরাধ বা ট্রোলের কারণ লিখুন:", placeholder="যেমন: ক্লায়েন্টকে ফ্রি ডেমো দিতে চেয়েছিল!")
                
                if st.button("🔨 রায় ঘোষণা করুন (আসামি লিস্টে পাঠান)", use_container_width=True):
                    if crime_note.strip():
                        asami_list[target_suspect] = {
                            "crime": crime_note.strip(),
                            "judge": "MD Reyadh [CEO 👑]",
                            "date": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        }
                        save_json_file(ASAMI_DB, asami_list)
                        st.success(f"🚓 {users[target_suspect].get('name')} সফলভাবে লকআপে চালান হয়েছে!")
                        time.sleep(0.5); st.rerun()
            
            with c_col2:
                st.markdown("#### 🕊️ আসামি খালাস/মাফ করুন:")
                if asami_list:
                    free_suspect = st.selectbox("কাকে মুক্তি দিবেন?", options=list(asami_list.keys()))
                    if st.button("🔓 জেল থেকে মুক্তি দিন", use_container_width=True):
                        del asami_list[free_suspect]
                        save_json_file(ASAMI_DB, asami_list)
                        st.success("আসামিকে সাধারণ ক্ষমার আওতায় মুক্তি দেওয়া হলো।")
                        time.sleep(0.5); st.rerun()
                else:
                    st.write("জেলে কোনো আসামি নাই।")
            
            st.markdown("---")
            # বাকি অ্যাডমিন কনফিগ
            new_notice = st.text_area("মেইন পেজের নোটিশ:", value=config.get("notice_text", ""))
            new_pin = st.text_input("২-ডিজিট মাস্টার পিন:", value=config.get("master_pin", "69"), max_chars=2)
            if st.button("কনফিগারেশন সেভ করুন 💾"):
                config["notice_text"] = new_notice; config["master_pin"] = new_pin
                save_json_file(CONFIG_FILE, config); st.success("✅ চেঞ্জড!")
        else:
            st.error("🔒 এই সেকশনটি শুধুমাত্র মেইন সিইও পোর্টাল দিয়ে লগইন করলেই এক্সেস করা যাবে।")

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v39.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
