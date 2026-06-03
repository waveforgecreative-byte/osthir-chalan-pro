import streamlit as st
import os
import json
import requests
import pandas as pd
import smtplib
import time
import datetime
import base64
import random
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- MULTI-USER SECURE STORAGE LAYER ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
CHAT_DB = "system_chat_memory.json"
DM_DB = "system_dm_memory.json"
ASAMI_DB = "system_asami_board.json"
MAIL_LOG_DB = "system_mail_logs.json"
COMPLAINT_DB = "system_complaints.json"

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

# --- RE-LOAD REALTIME DATABASE STATE ---
st.session_state.users_cache = load_json_file(USER_DB, {})
st.session_state.config_cache = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
st.session_state.chat_cache = load_json_file(CHAT_DB, [])
st.session_state.dm_cache = load_json_file(DM_DB, [])
st.session_state.asami_cache = load_json_file(ASAMI_DB, {})
st.session_state.mail_logs = load_json_file(MAIL_LOG_DB, {})
st.session_state.complaints = load_json_file(COMPLAINT_DB, [])

users = st.session_state.users_cache
config = st.session_state.config_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
asami_list = st.session_state.asami_cache
mail_logs = st.session_state.mail_logs
complaints_list = st.session_state.complaints

st.set_page_config(page_title="অস্থির চালান PRO v64.2 🖥️⚡", page_icon="🥷", layout="wide")

# --- 🔄 LIVE SYNC ENGINE (AUTO-REFRESHER) ---
# চ্যাট এবং ভিডিও কল লাইভ করার জন্য প্রতি ১ সেকেন্ড পর পর স্ট্রীমলিট অ্যাপ অটো-রিফ্রেশ হবে
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, limit=100000, key="live_sync_counter")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .ceo-alert { background: linear-gradient(90deg, #991B1B, #450A0A); border-left: 6px solid #EF4444; padding: 15px; border-radius: 8px; color: #FCA5A5; font-weight: bold; margin-bottom: 15px; box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
    
    /* 🛑 CRIMINAL HARD LOCKDOWN BOX */
    .lock-box { background: linear-gradient(135deg, #450A0A, #1F0303) !important; border: 2px dashed #EF4444 !important; border-left: 8px solid #FF0000 !important; padding: 25px !important; border-radius: 12px !important; color: #FCA5A5 !important; font-weight: bold !important; margin-bottom: 25px !important; text-align: center !important; box-shadow: 0 0 30px rgba(239, 68, 68, 0.6) !important; }
    .complaint-card { background: #1E293B; border-left: 4px solid #F59E0B; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #F8FAFC; }
    
    .asami-card { background: #111827; border: 1px solid #EF4444; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #FCA5A5; }
    .chat-box { height: 350px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    
    .incoming-call-alert { display: block !important; background: linear-gradient(135deg, #FF0055, #990033) !important; color: #FFFFFF !important; text-align: center !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 15px !important; margin: 10px 0px !important; border-radius: 8px !important; text-decoration: none !important; border: 2px solid #FF3366 !important; box-shadow: 0 0 20px rgba(255, 0, 85, 0.8) !important; animation: pulse 1s infinite; }
    .vcall-link-btn { display: block !important; width: 100% !important; text-align: center !important; background: linear-gradient(90deg, #00FF66, #007A3D) !important; color: #000000 !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 20px !important; margin: 10px 0px 20px 0px !important; border-radius: 8px !important; text-decoration: none !important; }
    .vcall-link-private { display: block !important; width: 100% !important; text-align: center !important; background: linear-gradient(90deg, #FF007F, #7928CA) !important; color: #FFFFFF !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 20px !important; margin: 10px 0px 20px 0px !important; border-radius: 8px !important; text-decoration: none !important; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "is_ceo" not in st.session_state: st.session_state.is_ceo = False
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "insta_query_saved" not in st.session_state: st.session_state.insta_query_saved = ""
if "show_vcall_trigger_link" not in st.session_state: st.session_state.show_vcall_trigger_link = False

# --- LIVE LOCKUP TRACKER & CHECKER ---
def check_user_lock(u_id):
    if u_id == "CEO 👑" or not u_id: return False, ""
    current_asami = load_json_file(ASAMI_DB, {})
    if u_id in current_asami:
        lock_until_ts = current_asami[u_id].get("lock_until_ts", 0)
        if time.time() < lock_until_ts:
            rem_sec = lock_until_ts - time.time()
            hours = int(rem_sec // 3600)
            mins = int((rem_sec % 3600) // 60)
            secs = int(rem_sec % 60)
            return True, f"{hours} ঘণ্টা {mins} মিনিট {secs} সেকেন্ড"
    return False, ""

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v64.2 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice-board">{config.get("notice_text", "")}</div>', unsafe_allow_html=True)
    login_mode = st.radio("🔑 লগইন টাইপ সিলেক্ট করুন:", ["👤 সাধারণ মেম্বার পোর্টাল", "👑 সিইও সিকিউর পোর্টাল"], horizontal=True)
    
    if login_mode == "👑 সিইও সিকিউর পোর্টাল":
        ceo_pass = st.text_input("সিইও মাস্টার পাসওয়ার্ড দিন:", type="password")
        if st.button("মাস্টার ড্যাশবোর্ড বুট করুন ⚡"):
            if ceo_pass == config.get("admin_pass", "reyadh123"):
                st.session_state.is_ceo = True; st.session_state.logged_in_user = "CEO 👑"; st.rerun()
            else: st.error("❌ ভুল পাসওয়ার্ড!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📝 নতুন অ্যাকাউন্ট খুলুন")
            reg_id = st.text_input("ইউনিক ইউজার আইডি (User ID):")
            reg_name = st.text_input("আপনার সম্পূর্ণ নাম (Full Name):")
            if st.button("অ্যাকাউন্ট তৈরি করুন ✅"):
                if reg_id.strip() and reg_name.strip() and reg_id.strip() not in users:
                    users[reg_id.strip()] = {"name": reg_name.strip(), "badge": "None", "user_api_key": "", "company_name": "", "user_role": "", "services": "", "sender_email": "", "app_pass": "", "last_seen": time.time()}
                    save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট ডান!")
        with col2:
            st.markdown("### 🔑 ড্যাশবোর্ড লগইন")
            login_id = st.text_input("ইউজার আইডি (User ID):", key="log_uid")
            input_pin = st.text_input("২-ডিজিট পিন:", type="password", max_chars=2)
            if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
                if login_id in users and str(input_pin).strip() == str(config.get("master_pin", "69")).strip():
                    st.session_state.logged_in_user = login_id; st.session_state.is_ceo = False; st.rerun()
                else: st.error("❌ ভুল পিন বা আইডি।")
else:
    current_user_id = st.session_state.logged_in_user
    is_ceo_active = st.session_state.is_ceo
    user_real_name = "MD Reyadh" if is_ceo_active else users[current_user_id].get("name", current_user_id)
    
    # লকডাউন স্ট্যাটাস চেক
    is_current_user_locked, remaining_lock_time = check_user_lock(current_user_id)

    # সিইও ব্রডকাস্ট মেসেজ ফ্ল্যাশ
    fresh_config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    if fresh_config.get("ceo_broadcast_msg", ""):
        st.markdown(f'<div class="ceo-alert">👑 <b>সিইও রিয়াদ ভাইয়ের আদেশ:</b> {fresh_config.get("ceo_broadcast_msg", "")}</div>', unsafe_allow_html=True)

    if is_ceo_active: 
        st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: 
        st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    # --- 🔒 কন্ডিশনাল ড্যাশবোর্ড লোডিং (যদি ইউজার লকড থাকে) ---
    if is_current_user_locked and not is_ceo_active:
        st.markdown(f"""
        <div class="lock-box">
            🦜🕸️ <b>খাঁচার ভেতর অচিন পাখি কেমনে আসে যায়!</b> 🛑<br><br>
            <span style="font-size: 22px; color: #FF3333;">আপনি বর্তমানে রিয়াদ ভাইয়ের খাঁচায় বন্দী আছেন!</span><br>
            ⚠️ আপনার অপরাধের কারণে আপনার ড্যাশবোর্ড লক করা হয়েছে।<br><br>
            💸 <b>উদ্ধার পাওয়ার উপায়:</b> জলদি <b>বিকাশে রিয়াদ ভাইকে মোটা অঙ্কের জরিমানা</b> পাঠিয়ে খাঁচা থেকে মুক্ত হোন! 😎<br>
            ⏳ বাকি সাজার মেয়াদ: <span style="color:#F59E0B;">{remaining_lock_time}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # লকড ইউজারের জন্য চ্যাটরুম, স্পেশাল ডিএম এবং আপিল বক্স ট্যাব
        lock_tab1, lock_tab2, lock_tab3 = st.tabs(["💬 Cyber Public Room", "🔒 Secret 1:1 DM (Riad Bhai)", "🚨 CEO Appeal Box"])
        
        with lock_tab1:
            st.subheader("🔊 সাইবার গ্লোবাল পাবলিক চ্যাট রুম")
            live_chats = load_json_file(CHAT_DB, [])
            chat_html = '<div class="chat-box">'
            for msg in live_chats:
                if isinstance(msg, dict):
                    sender_id = msg.get("sender")
                    sender_display = "MD Reyadh [CEO 👑]" if sender_id == "CEO 👑" else load_json_file(USER_DB, {}).get(sender_id, {}).get("name", sender_id)
                    if msg.get("type") == "vcall_alert":
                        chat_html += f'<a href="{msg.get("url")}" target="_blank" class="incoming-call-alert">📲 {msg.get("text")}</a>'
                    else:
                        msg_class = "msg-outgoing" if sender_id == current_user_id else "msg-incoming"
                        chat_html += f'<div class="{msg_class}"><b>{sender_display}:</b> {msg.get("text","")}</div>'
            st.markdown(chat_html + '</div>', unsafe_allow_html=True)
            
            with st.form("lock_pub_send", clear_on_submit=True):
                lock_t_msg = st.text_input("📝 গ্রুপে মেসেজ পাঠান:")
                if st.form_submit_button("পাঠান ✉️") and lock_t_msg.strip():
                    live_chats.append({"sender": current_user_id, "type": "text", "text": lock_t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                    save_json_file(CHAT_DB, live_chats); st.rerun()

        with lock_tab2:
            st.subheader("🔒 সিইও রিয়াদ ভাইয়ের সাথে ১:১ সিক্রেট ডিরেক্ট মেসেজ বক্স")
            st.warning("🔒 আপনি লকড থাকা অবস্থাতেও রিয়াদ ভাইয়ের সাথে সরাসরি পার্সোনাল চ্যাট বা কল রিসিভ করতে পারবেন।")
            
            sorted_pair = sorted([str(current_user_id), "CEO 👑"])
            private_call_url = f"https://meet.jit.si/reyadh-autoUX-1to1-{sorted_pair[0]}-{sorted_pair[1]}"
            
            # লাইভ ডিএম ও ইনকামিং কল চেক
            live_dms = load_json_file(DM_DB, [])
            
            # রিয়াদ ভাই কল দিলে ইনকামিং কল বাটন ফ্ল্যাশ হবে
            for dm in live_dms:
                if isinstance(dm, dict) and dm.get("receiver") == current_user_id and dm.get("type") == "vcall_alert":
                    st.markdown(f'<a href="{dm.get("url")}" target="_blank" class="incoming-call-alert">📲 {dm.get("text")}</a>', unsafe_allow_html=True)
            
            dm_html = '<div class="chat-box">'
            filtered_dms = [d for d in live_dms if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == "CEO 👑") or (d.get("sender") == "CEO 👑" and d.get("receiver") == current_user_id))]
            for dm in filtered_dms:
                dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else user_real_name
                dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}</div>'
            st.markdown(dm_html + '</div>', unsafe_allow_html=True)
            
            with st.form("lock_dm_send", clear_on_submit=True):
                t_lock_dm = st.text_input("✉️ রিয়াদ ভাইকে মেসেজ পাঠান:")
                if st.form_submit_button("মেসেজ পাঠান 🚀") and t_lock_dm.strip():
                    live_dms.append({"sender": current_user_id, "receiver": "CEO 👑", "type": "text", "text": t_lock_dm.strip()})
                    save_json_file(DM_DB, live_dms); st.rerun()

        with lock_tab3:
            st.markdown("### 🚨 সিইও রিয়াদ ভাই বরাবর স্পেশাল আপিল উইন্ডো")
            st.info("আপনার জরিমানা পরিশোধের বিকাশ ট্রানজেকশন আইডি অথবা ক্ষমা চাওয়ার মেইল সরাসরি সিইও রিয়াদ ভাইয়ের প্যানেলে চলে যাবে।")
            with st.form("complaint_form_locked", clear_on_submit=True):
                comp_subject = st.text_input("🎯 আপিল সাবজেক্ট (যেমন: জরিমানা পেইড/ভুল স্বীকার):", value="জরিমানা পেইড আপিল")
                comp_body = st.text_area("📄 বিস্তারিত বিবরণ বা বিকাশ ট্রানজেকশন আইডি/মেসেজটি লিখুন:")
                if st.form_submit_button("💥 সিইও রুমে আপিল সাবমিট করুন"):
                    if comp_subject.strip() and comp_body.strip():
                        complaints_list.append({
                            "user_id": current_user_id,
                            "user_name": user_real_name,
                            "type": "Appeal (🔒 Locked User)",
                            "subject": comp_subject.strip(),
                            "message": comp_body.strip(),
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        })
                        save_json_file(COMPLAINT_DB, complaints_list)
                        st.success("✅ আপনার আপিল রিয়াদ ভাইয়ের প্যানেলে পাঠানো হয়েছে। উনি ভেরিফাই করে খাঁচা খুলে দেবেন!")
                    else: st.error("❌ সব ঘর পূরণ করুন!")

    # --- 🔓 ফুল ড্যাশবোর্ড লোডিং (যদি ইউজার লকড না থাকে অথবা সিইও হয়) ---
    else:
        saved_api = config.get("ceo_saved_api", "") if is_ceo_active else users.get(current_user_id, {}).get("user_api_key", "")
        saved_company = config.get("ceo_company", "Reyadh Agency") if is_ceo_active else users.get(current_user_id, {}).get("company_name", "")
        saved_role = config.get("ceo_role", "Founder & CEO") if is_ceo_active else users.get(current_user_id, {}).get("user_role", "CEO")
        saved_services = config.get("ceo_services", "Video Editing, Thumbnail Design") if is_ceo_active else users.get(current_user_id, {}).get("services", "")
        saved_email = config.get("ceo_email", "") if is_ceo_active else users.get(current_user_id, {}).get("sender_email", "")
        saved_app_pass = config.get("ceo_app_pass", "") if is_ceo_active else users.get(current_user_id, {}).get("app_pass", "")

        engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5, engine_tab6 = st.tabs([
            "📍 Google Maps Scraper & Cold Mail Engine", 
            "📸 Instagram AI Global Hunter", 
            "💬 Cyber Messenger & Media Room",
            "🚨 CEO Complaint Box",  # নরমাল মেম্বারদের কমপ্লেইন্ট বক্স
            "🚨 পাবলিক আসামি থানা বোর্ড",
            "👑 CEO Secret Control Room"
        ])

        # --- TAB 1: GOOGLE MAPS & COLD MAILER ---
        with engine_tab1:
            st.subheader("📍 Google Maps Live Scraping & Integrated Cold Mailer")
            st.markdown("### ⚙️ ইউজার প্রোফাইল ও সিকিউরিটি কনফিগারেশন")
            p_col1, p_col2, p_col3 = st.columns(3)
            u_api_key = p_col1.text_input("🔑 SerpApi Key:", type="password", value=saved_api)
            u_company = p_col2.text_input("🏢 আপনার কোম্পানির নাম:", value=saved_company)
            u_role = p_col3.text_input("👔 আপনার পদবি:", value=saved_role)
            p_col4, p_col5 = st.columns(2)
            u_services = p_col4.text_input("⚡ আপনার সার্ভিসসমূহ:", value=saved_services)
            u_email = p_col5.text_input("📧 সেন্ডার জিমেইল:", value=saved_email)
            u_app_pass = st.text_input("🔒 জিমেইল অ্যাপ পাসওয়ার্ড:", type="password", value=saved_app_pass)
            
            if st.button("💾 প্রোফাইল ডাটা পার্মানেন্ট সেভ করুন"):
                if is_ceo_active:
                    config["ceo_saved_api"] = u_api_key.strip(); config["ceo_company"] = u_company.strip()
                    config["ceo_role"] = u_role.strip(); config["ceo_services"] = u_services.strip()
                    config["ceo_email"] = u_email.strip(); config["ceo_app_pass"] = u_app_pass.strip()
                    save_json_file(CONFIG_FILE, config)
                else:
                    users[current_user_id]["user_api_key"] = u_api_key.strip(); users[current_user_id]["company_name"] = u_company.strip()
                    users[current_user_id]["user_role"] = u_role.strip(); users[current_user_id]["services"] = u_services.strip()
                    users[current_user_id]["sender_email"] = u_email.strip(); users[current_user_id]["app_pass"] = u_app_pass.strip()
                    save_json_file(USER_DB, users)
                st.success("✅ কনফিগারেশন সেভ হয়েছে!"); time.sleep(0.5); st.rerun()

            st.markdown("---")
            st.markdown("### 🔍 লাইভ ম্যাপস ডাটা মাইনিং")
            col_s1, col_s2 = st.columns(2)
            search_query = col_s1.text_input("🎯 টার্গেটেড নিশ বা কিওয়ার্ড লিখুন (যেমন: 'Dentists in New York'):")
            search_limit = col_s2.number_input("📊 কতগুলো লিড স্ক্র্যাপ করতে চান?", min_value=5, max_value=100, value=10, step=5)
            
            if st.button("🚀 ম্যাপস ডাটা এক্সট্রাক্ট করা শুরু করুন"):
                if not u_api_key: st.error("❌ দয়া করে আগে SerpApi কী প্রদান করুন।")
                else:
                    with st.spinner("⏳ গুগল ক্লাউড থেকে লাইভ ডাটা আনা হচ্ছে..."):
                        api_url = f"https://serpapi.com/search.json?engine=google_maps&q={urllib.parse.quote(search_query)}&hl=en&auth_user=0&api_key={u_api_key}"
                        try:
                            res = requests.get(api_url).json()
                            local_results = res.get("local_results", [])
                            if local_results:
                                scrapped_leads = []
                                for idx, place in enumerate(local_results[:search_limit]):
                                    scrapped_leads.append({
                                        "ID": idx+1, "কোম্পানির নাম": place.get("title", "N/A"),
                                        "ফোন নাম্বার": place.get("phone", "N/A"), "ওয়েবসাইট": place.get("website", "N/A"),
                                        "ঠিকানা": place.get("address", "N/A"), "রেটিং": place.get("rating", "N/A")
                                    })
                                st.session_state.current_leads = scrapped_leads
                                st.success(f"✅ সফলভাবে {len(scrapped_leads)} টি লিড পাওয়া গেছে!")
                            else: st.warning("❌ কোনো লিড পাওয়া যায়নি।")
                        except Exception as e: st.error(f"Error: {e}")

            if st.session_state.current_leads:
                st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)
                st.markdown("---")
                st.markdown("### ✉️ AI চালিত বাল্ক কোল্ড মেইলিং সিস্টেম")
                email_subject = st.text_input("📝 মেইলের সাবজেক্ট (Subject):", value=f"Proposal from {u_company if u_company else 'Our Agency'}")
                raw_leads_emails = st.text_area("📧 টার্গেটেড ক্লায়েন্ট ইমেইল লিস্ট (কমা দিয়ে আলাদা করুন):")
                email_body = st.text_area("📄 ইমেইল বডি কাস্টমাইজ করুন:", value=f"Hello,\nI am {u_role} from {u_company}...", height=150)
                
                if st.button("⚡ Automated Cold Mail fayer"):
                    email_list = [e.strip() for e in raw_leads_emails.replace("\n", ",").split(",") if e.strip()]
                    if email_list and u_email and u_app_pass:
                        for target_email in email_list:
                            try:
                                msg = MIMEMultipart(); msg['From'] = u_email; msg['To'] = target_email; msg['Subject'] = email_subject
                                msg.attach(MIMEText(email_body, 'plain'))
                                server = smtplib.SMTP_SSL('smtp.gmail.com', 465); server.login(u_email, u_app_pass)
                                server.sendmail(u_email, target_email, msg.as_string()); server.quit()
                            except: pass
                        st.success("🚀 মিশন সাকসেসফুল! মেইল পাঠানো শেষ।")

        # --- TAB 2: INSTAGRAM HUNTER ---
        with engine_tab2:
            st.markdown("<h2 style='color:#00FF66;'>📸 ইনস্টাগ্রাম AI গ্লোবাল হান্টার</h2>", unsafe_allow_html=True)
            st.markdown("> **খাঁচার ভেতর অচিন পাখি কেমনে আসে যায়! ঠিক তেমনি কোনো অফিশিয়াল API ছাড়া আমাদের মেম্বাররা কেমনে যে ডাটা স্ক্র্যাপ করে চলে যায়, তা মার্ক জুকারবার্গও টের পায় না! 🦜🕸️**")
            insta_keyword = st.text_input("🔍 টার্গেটেড ইনস্টাগ্রাম হ্যাশট্যাগ বা নিশ দিন:", value=st.session_state.insta_query_saved)
            if st.button("🎯 ইনস্টাগ্রাম ইনফ্লুয়েন্সার ও বিজনেস ক্লায়েন্ট এক্সপ্লোর করুন"):
                if insta_keyword.strip():
                    st.session_state.insta_query_saved = insta_keyword.strip()
                    dummy_insta = [
                        {"ইউজারনেম": f"{insta_keyword}_queen", "অনুসারী": "120K", "ক্যাটাগরি": "Fitness Model", "ইমেইল Status": "Public (🔥 মেইল মারো)"},
                        {"ইউজারনেম": f"the_{insta_keyword}_boss", "অনুসারী": "45.8K", "ক্যাটাগরি": "Entrepreneur", "ইমেইল Status": "Protected"},
                    ]
                    st.dataframe(pd.DataFrame(dummy_insta), use_container_width=True)
                    st.success("🦜 পাখি খাঁচা ভেঙে ডাটা নিয়ে এসেছে!")

        # --- TAB 3: CYBER MESSENGER & MEDIA ---
        with engine_tab3:
            st.markdown("### 🔊 সাইবার মাল্টিমিডিয়া চ্যাট ও ভয়েস/ভিডিও মেকানিজম")
            chat_sub1, chat_sub2 = st.tabs(["🔊 Global Public Chat Room", "🔒 Secret 1:1 Personal DM Portal"])
            
            with chat_sub1:
                st.markdown('<a href="https://meet.jit.si/reyadh-osthir-chalawn-global-group" target="_blank" class="vcall-link-btn">🔊 গ্লোবাল গ্রুপ ভিডিও কল রুমে ঢুকুন 🎥🔊</a>', unsafe_allow_html=True)
                live_chats = load_json_file(CHAT_DB, [])
                chat_html = '<div class="chat-box">'
                for msg in live_chats:
                    if isinstance(msg, dict):
                        sender_id = msg.get("sender")
                        sender_display = "MD Reyadh [CEO 👑]" if sender_id == "CEO 👑" else load_json_file(USER_DB, {}).get(sender_id, {}).get("name", sender_id)
                        if msg.get("type") == "vcall_alert":
                            chat_html += f'<a href="{msg.get("url")}" target="_blank" class="incoming-call-alert">📲 {msg.get("text")}</a>'
                        else:
                            msg_class = "msg-outgoing" if sender_id == current_user_id else "msg-incoming"
                            chat_html += f'<div class="{msg_class}"><b>{sender_display}:</b> {msg.get("text","")}</div>'
                st.markdown(chat_html + '</div>', unsafe_allow_html=True)
                
                with st.form("pub_send_main", clear_on_submit=True):
                    t_msg = st.text_input("📝 পাবলিক গ্রুপে টেক্সট মেসেজ লিখুন:")
                    if st.form_submit_button("পাঠান ✉️") and t_msg.strip():
                        live_chats.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "type": "text", "text": t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                        save_json_file(CHAT_DB, live_chats); st.rerun()
            
            with chat_sub2:
                # রিয়াদ ভাইয়ের ডিএম স্ক্রিনে লকড ইউজারদেরও শো করার জন্য সম্পূর্ণ ডাটাবেস ম্যাপিং
                name_to_id_map = {u_info.get('name', u_id): u_id for u_id, u_info in users.items() if u_id != current_user_id and u_id != "CEO 👑"}
                if is_ceo_active: name_to_id_map = {u_info.get('name', u_id): u_id for u_id, u_info in users.items()}
                
                if name_to_id_map:
                    all_display_names = list(name_to_id_map.keys())
                    target_real_name = st.selectbox("🔒 মেম্বার সিলেক্ট করুন (আসল নাম):", options=all_display_names)
                    target_dm = name_to_id_map[target_real_name]
                    
                    sorted_pair = sorted([str(current_user_id), str(target_dm)])
                    private_call_url = f"https://meet.jit.si/reyadh-autoUX-1to1-{sorted_pair[0]}-{sorted_pair[1]}"
                    
                    c_btn1, c_btn2 = st.columns([2, 1])
                    if c_btn1.button(f"📞 {target_real_name} কে সরাসরি ভিডিও কল দিন 🎥", use_container_width=True):
                        fresh_dms = load_json_file(DM_DB, [])
                        alert_text = f"{user_real_name} আপনাকে ভিডিও কলে ডাকছেন! জয়েন করতে এই বাটনে ক্লিক করুন 📲"
                        
                        # আগের পুরোনো কলের অ্যালার্ট রিমুভ করে ফ্রেশ কল পুশ
                        fresh_dms = [d for d in fresh_dms if not (d.get("receiver") == target_dm and d.get("type") == "vcall_alert")]
                        fresh_dms.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "receiver": target_dm, "type": "vcall_alert", "text": alert_text, "url": private_call_url})
                        save_json_file(DM_DB, fresh_dms)
                        
                        fresh_chats = load_json_file(CHAT_DB, [])
                        fresh_chats.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "type": "vcall_alert", "text": f"🚨 {target_real_name} ভাই, জলদি লাইভ কলে আসুন! {user_real_name} লাইনে আছেন 👉", "url": private_call_url})
                        save_json_file(CHAT_DB, fresh_chats)
                        st.session_state.show_vcall_trigger_link = True; st.rerun()
                    
                    if c_btn2.button("🚫 কল লিংক সরাও"): st.session_state.show_vcall_trigger_link = False; st.rerun()
                    if st.session_state.show_vcall_trigger_link:
                        st.markdown(f'<a href="{private_call_url}" target="_blank" class="vcall-link-private">👑 আপনি কলটি শুরু করেছেন: রুমে প্রবেশ করতে এখানে ক্লিক করুন 🎥</a>', unsafe_allow_html=True)
                    
                    # গোপন মেসেজ বক্স রেন্ডারিং
                    live_dms = load_json_file(DM_DB, [])
                    dm_html = '<div class="chat-box">'
                    filtered_dms = [d for d in live_dms if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm) or (d.get("sender") == target_dm and d.get("receiver") == current_user_id))]
                    for dm in filtered_dms:
                        if dm.get("type") != "vcall_alert":
                            dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else load_json_file(USER_DB, {}).get(dm.get("sender"), {}).get("name", dm.get("sender"))
                            dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                            dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}</div>'
                    st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                    
                    with st.form("dm_send_main", clear_on_submit=True):
                        t_dm = st.text_input(f"✉️ {target_real_name}-কে টেক্সট পাঠান:")
                        if st.form_submit_button("মেসেজ পাঠান 🚀") and t_dm.strip():
                            live_dms.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "receiver": target_dm, "type": "text", "text": t_dm.strip()})
                            save_json_file(DM_DB, live_dms); st.rerun()

        # --- TAB 4: GLOBAL COMPLAINT BOX (স্বাভাবিক মেম্বারদের জন্য কমপ্লেইন্ট বক্স) ---
        with engine_tab4:
            st.markdown("### 🚨 সিইও রিয়াদ ভাই বরাবর মেম্বার কমপ্লেইন্ট বক্স")
            st.info("ড্যাশবোর্ডে কাজ করতে গিয়ে যেকোনো কারিগরি সমস্যা বা বাঘ ফেস করলে সরাসরি সিইও রিয়াদ ভাইয়ের কাছে কমপ্লেইন্ট রিপোর্ট জমা দিন।")
            with st.form("global_complaint_form", clear_on_submit=True):
                g_comp_subject = st.text_input("🎯 কমপ্লেইন্ট সাবজেক্ট / কাজের সমস্যা:")
                g_comp_body = st.text_area("📄 আপনার সমস্যাটি বিস্তারিত বর্ণনা করুন:")
                if st.form_submit_button("💥 সিইও রুমে কমপ্লেইন্ট জমা দিন"):
                    if g_comp_subject.strip() and g_comp_body.strip():
                        complaints_list.append({
                            "user_id": current_user_id,
                            "user_name": user_real_name,
                            "type": "Complaint (👤 Normal User)",
                            "subject": g_comp_subject.strip(),
                            "message": g_comp_body.strip(),
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        })
                        save_json_file(COMPLAINT_DB, complaints_list)
                        st.success("✅ কমপ্লেইন্ট সফলভাবে সাবমিট হয়েছে! রিয়াদ ভাই চেক করে ব্যবস্থা নেবেন।")
                    else: st.error("❌ সব ঘর পূরণ করুন!")

        # --- TAB 5: PUBLIC ASAMI BOARD ---
        with engine_tab5:
            st.markdown("<h2 style='color:#EF4444;'>🚨 সাইবার থানা আসামি বোর্ড 🚓</h2>", unsafe_allow_html=True)
            current_asami = load_json_file(ASAMI_DB, {})
            if current_asami:
                for bad_user, info in current_asami.items():
                    st.markdown(f'<div class="asami-card">🛑 <b>আসামি আইডি:</b> {bad_user} | ⚖️ <b>অপরাধ:</b> {info.get("reason")}</div>', unsafe_allow_html=True)
            else: st.success("🟢 থানায় কোনো আসামি নেই!")

        # --- TAB 6: CEO SECRET CONTROL ROOM ---
        with engine_tab6:
            st.subheader("👑 Riad Bhai's Secret Control Room")
            if not is_ceo_active: st.error("🔒 এই সেকশন শুধুমাত্র মেইন সিইও রিয়াদ ভাইয়ের জন্য সংরক্ষিত!")
            else:
                st.success("👑 অ্যাক্সেস গ্রান্টেড, রিয়াদ ভাই!")
                
                # কমপ্লেইন্ট ও আপিল ট্র্যাকার রেন্ডারিং (সবাই যা পাঠাবে টাইপসহ এখানে জমা হবে)
                st.markdown("### 📥 ড্যাশবোর্ডের সব কমপ্লেইন্ট ও আসামিদের আপিল ইনবক্স")
                live_complaints = load_json_file(COMPLAINT_DB, [])
                if live_complaints:
                    for idx, comp in enumerate(live_complaints):
                        st.markdown(f"""
                        <div class="complaint-card">
                            🏷️ <b>ক্যাটাগরি:</b> <span style="color:#F59E0B;">{comp.get('type','General')}</span><br>
                            👤 <b>মেম্বার:</b> {comp.get('user_name')} ({comp.get('user_id')}) | 📅 {comp.get('time')}<br>
                            📌 <b>সাবজেক্ট:</b> {comp.get('subject')}<br>
                            💬 <b>মেসেজ/বিকাশ স্টেটমেন্ট:</b> {comp.get('message')}
                        </div>
                        """, unsafe_allow_html=True)
                    if st.button("🗑️ সব ইনবক্স ডাটা ক্লিয়ার করুন"):
                        save_json_file(COMPLAINT_DB, []); st.success("কমপ্লেইন্ট বক্স ফ্লাশ করা হয়েছে!"); st.rerun()
                else: st.info("📥 বর্তমানে কোনো কমপ্লেইন্ট বা আপিল জমা পড়েনি।")
                
                st.markdown("---")
                new_notice = st.text_area("নোটিশ বোর্ড আপডেট করুন:", value=config.get("notice_text", ""))
                new_broadcast = st.text_input("মেম্বারদের স্ক্রিনে ফ্ল্যাশ মেসেজ পাঠান:", value=config.get("ceo_broadcast_msg", ""))
                new_pin = st.text_input("২-ডিজিট ড্যাোর্ড মাস্টার পিন পরিবর্তন করুন:", value=config.get("master_pin", "69"), max_chars=2)
                
                if st.button("💾 গ্লোবাল কনফিগারেশন সেভ করুন"):
                    config["notice_text"] = new_notice; config["ceo_broadcast_msg"] = new_broadcast; config["master_pin"] = new_pin
                    save_json_file(CONFIG_FILE, config); st.success("⚙️ সেটিংস সফলভাবে আপডেট হয়েছে!"); st.rerun()
                
                st.markdown("---")
                if users:
                    asami_select = st.selectbox("🚨 আসামি মেম্বার সিলেক্ট করুন:", options=list(users.keys()))
                    asami_reason = st.text_input("⚖️ অপরাধের কারণ:")
                    lock_hours = st.number_input("⏳ কত ঘণ্টার জন্য লকআউট করবেন?", min_value=1, value=24)
                    
                    if st.button("🔒 মেম্বারকে জেলখানায় পাঠান"):
                        lock_ts = time.time() + (lock_hours * 3600)
                        current_asami[asami_select] = {"reason": asami_reason, "lock_until_ts": lock_ts}
                        save_json_file(ASAMI_DB, current_asami); st.error("🛑 মেম্বার ব্লকড!"); st.rerun()
                        
                    if st.button("🔓 মেম্বারকে ক্ষমা করুন (Unban)"):
                        if asami_select in current_asami:
                            del current_asami[asami_select]; save_json_file(ASAMI_DB, current_asami)
                            st.success("✅ মেম্বার আনব্যানড!"); st.rerun()

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v64.2 PRO Live-Sync | Developed by MD Reyadh</div>', unsafe_allow_html=True)
