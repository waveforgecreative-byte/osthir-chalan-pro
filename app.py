import streamlit as st
import os
import json
import requests
import pandas as pd
import smtplib
import time
import datetime
import urllib.parse
import re
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
LEADS_HISTORY_DB = "system_leads_history.json"

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

# Cache initialization
if "users_cache" not in st.session_state: st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state: st.session_state.config_cache = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "re_leads" not in st.session_state: st.session_state.re_leads = []
if "active_tab_index" not in st.session_state: st.session_state.active_tab_index = 0

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "is_ceo" not in st.session_state: st.session_state.is_ceo = False

users = st.session_state.users_cache
config = st.session_state.config_cache

st.set_page_config(page_title="অস্থির চালান PRO v65.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght=400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    .funny-warning { background: linear-gradient(135deg, #450A0A, #110303); border: 2px dashed #FF3333; padding: 15px; border-radius: 8px; color: #FF9999; text-align: center; font-weight: bold; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email)) and "example" not in email

def is_valid_phone(phone):
    if phone == "N/A" or not phone: return False
    clean_phone = re.sub(r'\D', '', phone)
    return len(clean_phone) >= 7

def fire_bulk_emails(leads_list, u_email, u_app_pass, email_subject, email_body):
    progress_bar = st.progress(0)
    status_text = st.empty()
    sent_now = 0
    
    for idx, lead in enumerate(leads_list):
        target_email = lead.get("রিয়েল ইমেইল" if "রিয়েল ইমেইল" in lead else "ইমেইল", "N/A")
        client_name = lead.get("কোম্পানির নাম" if "কোম্পানির নাম" in lead else "Client", "Client")
        
        if target_email == "N/A" or not target_email or not is_valid_email(target_email):
            continue
            
        current_logs = load_json_file(MAIL_LOG_DB, {})
        s_count = current_logs.get(u_email, 0)
        if s_count >= 100:
            st.error("🛑 ডেইলি মেইলিং লিমিট (১০০) শেষ হয়েছে!")
            break
            
        try:
            personalized_body = email_body.replace("{Name}", client_name)
            personalized_subject = email_subject.replace("{Name}", client_name)
            
            msg = MIMEMultipart()
            msg['From'] = u_email
            msg['To'] = target_email
            msg['Subject'] = personalized_subject
            msg.attach(MIMEText(personalized_body, 'plain'))
            
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(u_email, u_app_pass)
            server.sendmail(u_email, target_email, msg.as_string())
            server.quit()
            
            current_logs[u_email] = s_count + 1
            save_json_file(MAIL_LOG_DB, current_logs)
            sent_now += 1
        except Exception as e:
            pass
        
        percent = int(((idx + 1) / len(leads_list)) * 100)
        progress_bar.progress(percent)
        status_text.markdown(f"🚀 **টার্মিনাল ফায়ার:** `{client_name}` ➡️ ({target_email})")
        time.sleep(4)
        
    st.success(f"🔥 মিশন সাকসেসফুল! সম্পূর্ণ ফ্রেশ ডাটাতে {sent_now} টি সাকসেসফুল মেইল পাঠানো হয়েছে।")

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v65.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice-board">{config.get("notice_text", "")}</div>', unsafe_allow_html=True)
    login_mode = st.radio("🔑 লগইন টাইপ সিলেক্ট করুন:", ["👤 সাধারণ মেম্বার পোর্টাল", "👑 সিইও সিকিউর পোর্টাল"], horizontal=True)
    
    if login_mode == "👑 সিইও সিকিউর পোর্টাল":
        ceo_pass = st.text_input("সিইও মাস্টার পাসওয়ার্ড দিন:", type="password")
        if st.button("মাস্টার ড্যাশবোর্ড বুট করুন ⚡"):
            if ceo_pass == config.get("admin_pass", "reyadh123"):
                st.session_state.is_ceo = True; st.session_state.logged_in_user = "CEO 👑"; st.rerun()
            else: st.error("❌ ভুল পাসওয়ার্ড!")
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
                # পিন সঠিক কিনা চেক
                if login_id in users and str(input_pin).strip() == str(config.get("master_pin", "69")).strip():
                    st.session_state.logged_in_user = login_id; st.session_state.is_ceo = False; st.rerun()
                else:
                    st.markdown("""
                    <div class="funny-warning">
                        ❌ পিন হয় নাই মামা! এই সিকিউর ড্যাশবোর্ড আনলক করতে ২-ডিজিটের গোপন পিন লাগবে। <br>
                        পিন না জানলে সোজা <b>MD Reyadh</b> ভাইকে মেসেজ দিয়ে পিন চেয়ে নিন! 😉
                    </div>
                    """, unsafe_allow_html=True)
                    # আপনার ফেসবুক বা মেসেঞ্জারের লিঙ্ক এখানে বসিয়ে দিন
                    st.link_button("💬 রিয়াদ ভাইকে মেসেজ দিন", "https://m.me/your_messenger_id_here")

else:
    current_user_id = st.session_state.logged_in_user
    is_ceo_active = st.session_state.is_ceo
    user_real_name = "MD Reyadh" if is_ceo_active else users[current_user_id].get("name", current_user_id)
    
    if is_ceo_active: st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    saved_api = config.get("ceo_saved_api", "") if is_ceo_active else users.get(current_user_id, {}).get("user_api_key", "")
    saved_company = config.get("ceo_company", "Reyadh Agency") if is_ceo_active else users.get(current_user_id, {}).get("company_name", "")
    saved_role = config.get("ceo_role", "Founder & CEO")
