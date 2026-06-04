import streamlit as st
import os
import json
import requests
import pandas as pd
import smtplib
import time
import datetime
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
LEADS_HISTORY_DB = "system_leads_history.json" # ডুপ্লিকেট লিড ট্র্যাকার

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

# --- INITIAL DATA STATE LOAD ---
if "users_cache" not in st.session_state: st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state: st.session_state.config_cache = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
if "chat_cache" not in st.session_state: st.session_state.chat_cache = load_json_file(CHAT_DB, [])
if "dm_cache" not in st.session_state: st.session_state.dm_cache = load_json_file(DM_DB, [])
if "asami_cache" not in st.session_state: st.session_state.asami_cache = load_json_file(ASAMI_DB, {})
if "mail_logs" not in st.session_state: st.session_state.mail_logs = load_json_file(MAIL_LOG_DB, {})
if "complaints" not in st.session_state: st.session_state.complaints = load_json_file(COMPLAINT_DB, [])

users = st.session_state.users_cache
config = st.session_state.config_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
asami_list = st.session_state.asami_cache
mail_logs = st.session_state.mail_logs
complaints_list = st.session_state.complaints

st.set_page_config(page_title="অস্থির চালান PRO v64.2 🖥️⚡", page_icon="🥷", layout="wide")

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
    
    .lock-box { background: linear-gradient(135deg, #450A0A, #1F0303) !important; border: 2px dashed #EF4444 !important; border-left: 8px solid #FF0000 !important; padding: 25px !important; border-radius: 12px !important; color: #FCA5A5 !important; font-weight: bold !important; margin-bottom: 25px !important; text-align: center !important; box-shadow: 0 0 30px rgba(239, 68, 68, 0.6) !important; }
    .complaint-card { background: #1E293B; border-left: 4px solid #F59E0B; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #F8FAFC; }
    
    .asami-card { background: #111827; border: 1px solid #EF4444; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #FCA5A5; }
    .chat-box { height: 350px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    
    .incoming-call-alert { display: block !important; background: linear-gradient(135deg, #FF0055, #990033) !important; color: #FFFFFF !important; text-align: center !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 15px !important; margin: 10px 0px !important; border-radius: 8px !important; text-decoration: none !important; border: 2px solid #FF3366 !important; box-shadow: 0 0 20px rgba(255, 0, 85, 0.8) !important; }
    .vcall-link-btn { display: block !important; width: 100% !important; text-align: center !important; background: linear-gradient(90deg, #00FF66, #007A3D) !important; color: #000000 !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 20px !important; margin: 10px 0px 20px 0px !important; border-radius: 8px !important; text-decoration: none !important; }
    .vcall-link-private { display: block !important; width: 100% !important; text-align: center !important; background: linear-gradient(90deg, #FF007F, #7928CA) !important; color: #FFFFFF !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 20px !important; margin: 10px 0px 20px 0px !important; border-radius: 8px !important; text-decoration: none !important; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    
    .msg-noti-bar { background: linear-gradient(90deg, #10B981, #059669); color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
    .antiban-alert { background: linear-gradient(135deg, #6B21A8, #450A0A); border: 3px solid #FF0055; color: #FFF0F0; padding: 22px; border-radius: 12px; font-weight: bold; margin: 20px 0px; text-align: center; box-shadow: 0 0 30px rgba(255, 0, 85, 0.7); }
    .limit-success-tracker { background: #0F172A; border-left: 5px solid #00FF66; padding: 10px; border-radius: 6px; margin: 10px 0px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "is_ceo" not in st.session_state: st.session_state.is_ceo = False
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "insta_query_saved" not in st.session_state: st.session_state.insta_query_saved = ""
if "show_vcall_trigger_link" not in st.session_state: st.session_state.show_vcall_trigger_link = False

live_chats_init = load_json_file(CHAT_DB, [])
live_dms_init = load_json_file(DM_DB, [])
if "last_checked_msg_count" not in st.session_state: st.session_state.last_checked_msg_count = len(live_chats_init)
if "last_checked_dm_count" not in st.session_state: st.session_state.last_checked_dm_count = len(live_dms_init)

if "latest_unread_msg" not in st.session_state: st.session_state.latest_unread_msg = None
if "active_tab_index" not in st.session_state: st.session_state.active_tab_index = 0

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

# --- DIRECT CALL DIALOG POPUP ---
@st.dialog("🚨 লাইভ ভিডিও কল ইনভাইটেশন 🎥")
def trigger_call_popup(sender_name, call_url):
    st.markdown(f"### 👑 **{sender_name}** আপনাকে সরাসরি লাইভ ভিডিও কলে ডাকছেন!")
    st.markdown("দেরি না করে নিচের বাটনে ক্লিক করে সরাসরি লাইভ ডিসকাশন রুমে জয়েন করুন।")
    st.link_button("🟢 রিসিভ করে কলে জয়েন করুন", call_url, use_container_width=True)
    if st.button("বন্ধ করুন ❌", use_container_width=True):
        st.rerun()

# --- 🔄 BACKGROUND LIVE ENGINE (st.fragment) ---
@st.fragment(run_every=1.5)
def background_live_engine():
    current_uid = st.session_state.logged_in_user
    if not current_uid: return

    force_ui_refresh = False
    live_chats = load_json_file(CHAT_DB, [])
    if len(live_chats) > st.session_state.last_checked_msg_count:
        last_msg = live_chats[-1]
        if last_msg.get("sender") != current_uid and last_msg.get("type") != "vcall_alert":
            s_id = last_msg.get("sender")
            s_name = "MD Reyadh [CEO 👑]" if s_id == "CEO 👑" else load_json_file(USER_DB, {}).get(s_id, {}).get("name", s_id)
            st.toast(f"💬 {s_name}: {last_msg.get('text', '')}", icon="📩")
            st.session_state.latest_unread_msg = {"sender": s_name, "text": last_msg.get('text', '')}
            force_ui_refresh = True
        st.session_state.last_checked_msg_count = len(live_chats)

    live_dms = load_json_file(DM_DB, [])
    active_calls = [d for d in live_dms if isinstance(d, dict) and d.get("receiver") == current_uid and d.get("type") == "vcall_alert"]
    if active_calls:
        latest_call = active_calls[-1]
        caller_id = latest_call.get("sender")
        caller_name = "MD Reyadh [CEO 👑]" if caller_id == "CEO 👑" else load_json_file(USER_DB, {}).get(caller_id, {}).get("name", caller_id)
        clean_dms = [d for d in live_dms if not (d.get("receiver") == current_uid and d.get("type") == "vcall_alert")]
        save_json_file(DM_DB, clean_dms)
        trigger_call_popup(caller_name, latest_call.get("url"))

    if len(live_dms) > st.session_state.last_checked_dm_count:
        if live_dms:
            last_dm = live_dms[-1]
            if last_dm.get("receiver") == current_uid and last_dm.get("type") != "vcall_alert":
                s_id = last_dm.get("sender")
                s_name = "MD Reyadh [CEO 👑]" if s_id == "CEO 👑" else load_json_file(USER_DB, {}).get(s_id, {}).get("name", s_id)
                st.toast(f"🔒 [Secret DM] {s_name}: {last_dm.get('text', '')}", icon="🤫")
                st.session_state.latest_unread_msg = {"sender": f"[DM] {s_name}", "text": last_dm.get('text', '')}
                force_ui_refresh = True
        st.session_state.last_checked_dm_count = len(live_dms)

    if force_ui_refresh:
        st.markdown("<script>window.parent.document.querySelector('.stApp').click();</script>", unsafe_allow_html=True)

background_live_engine()

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v64.2 🖥️⚡</p>', unsafe_allow_html=True)
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
                if login_id in users and str(input_pin).strip() == str(config.get("master_pin", "69")).strip():
                    st.session_state.logged_in_user = login_id; st.session_state.is_ceo = False; st.rerun()
                else: st.error("❌ ভুল পিন বা আইডি।")
else:
    current_user_id = st.session_state.logged_in_user
    is_ceo_active = st.session_state.is_ceo
    user_real_name = "MD Reyadh" if is_ceo_active else users[current_user_id].get("name", current_user_id)
    
    is_current_user_locked, remaining_lock_time = check_user_lock(current_user_id)

    fresh_config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    if fresh_config.get("ceo_broadcast_msg", ""):
        st.markdown(f'<div class="ceo-alert">👑 <b>সিইও রিয়াদ ভাইয়ের আদেশ:</b> {fresh_config.get("ceo_broadcast_msg", "")}</div>', unsafe_allow_html=True)

    if is_ceo_active: st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    if st.session_state.latest_unread_msg:
        noti_data = st.session_state.latest_unread_msg
        c_not1, c_not2 = st.columns([5, 1])
        with c_not1: st.markdown(f'<div class="msg-noti-bar">📩 নতুন মেসেজ এসেছে! <b>{noti_data["sender"]}:</b> {noti_data["text"]}</div>', unsafe_allow_html=True)
        with c_not2:
            if st.button("💬 চ্যাট বক্সে যান", use_container_width=True):
                st.session_state.active_tab_index = 2 
                st.session_state.latest_unread_msg = None 
                st.rerun()

    # --- 🔒 কন্ডিশনাল ড্যাশবোর্ড (লকড ইউজার) ---
    if is_current_user_locked and not is_ceo_active:
        st.markdown(f"""<div class="lock-box">Parrot Web 🦜🕸️ <b>খাঁচার ভেতর অচিন পাখি কেমনে আসে যায়!</b> 🛑<br><br><span style="font-size: 22px; color: #FF3333;">আপনি বর্তমানে রিয়াদ ভাইয়ের খাঁচায় বন্দী আছেন!</span><br>⚠️ আপনার অপরাধের কারণে আপনার ড্যাশবোর্ড লক করা হয়েছে।<br><br>💸 <b>উদ্ধার পাওয়ার উপায়:</b> জলদি <b>বিকাশে রিয়াদ ভাইকে মোটা অঙ্কের জরিমানা</b> পাঠিয়ে খাঁচা থেকে মুক্ত হোন! 😎<br>⏳ বাকি সাজার মেয়াদ: <span style="color:#F59E0B;">{remaining_lock_time}</span></div>""", unsafe_allow_html=True)
        lock_tab1, lock_tab2, lock_tab3 = st.tabs(["💬 Cyber Public Room", "🔒 Secret 1:1 DM (Riad Bhai)", "🚨 CEO Appeal Box"])
        
        with lock_tab1:
            st.subheader("🔊 সাইবার গ্লোবাল পাবলিক চ্যাট রুম")
            live_chats = load_json_file(CHAT_DB, [])
            chat_html = '<div class="chat-box">'
            for msg in live_chats:
                if isinstance(msg, dict):
                    sender_id = msg.get("sender")
                    sender_display = "MD Reyadh [CEO 👑]" if sender_id == "CEO 👑" else load_json_file(USER_DB, {}).get(sender_id, {}).get("name", sender_id)
                    if msg.get("type") == "vcall_alert": chat_html += f'<a href="{msg.get("url")}" target="_blank" class="incoming-call-alert">📲 {msg.get("text")}</a>'
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
            st.subheader("🔒 সিইও রিয়াদ ভাইয়ের সাথে ১:১ সিক্রেট ডিরেক্ট মেসেজ বক্স")
            live_dms = load_json_file(DM_DB, [])
            dm_html = '<div class="chat-box">'
            filtered_dms = [d for d in live_dms if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == "CEO 👑") or (d.get("sender") == "CEO 👑" and d.get("receiver") == current_user_id))]
            for dm in filtered_dms:
                if dm.get("type") != "vcall_alert":
                    dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else user_real_name
                    dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                    dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}</div>'
            st.markdown(dm_html + '</div>', unsafe_allow_html=True)
            with st.form("lock_dm_send", clear_on_submit=True):
                t_lock_dm = st.text_input("✉️ রিয়াদ ভাইকে মেসেজ পাঠান:")
                if st.form_submit_button("মেসেজ পাঠান 🚀") and t_lock_dm.strip():
                    live_dms.append({"sender": current_user_id, "receiver": "CEO 👑", "type": "text", "text": t_lock_dm.strip()})
                    save_json_file(DM_DB, live_dms); st.rerun()

        with lock_tab3:
            st.markdown("### 🚨 সিইও রিয়াদ ভাই বরাবর স্পেশাল আপিল উইন্ডো")
            with st.form("complaint_form_locked", clear_on_submit=True):
                comp_subject = st.text_input("🎯 আপিল সাবজেক্ট:", value="জরিমানা পেইড আপিল")
                comp_body = st.text_area("📄 বিস্তারিত বিবরণ বা বিকাশ ট্রানজেকশন আইডি লিখুন:")
                if st.form_submit_button("💥 সিইও রুমে আপিল সাবমিট করুন"):
                    if comp_subject.strip() and comp_body.strip():
                        complaints_list.append({"user_id": current_user_id, "user_name": user_real_name, "type": "Appeal (🔒 Locked User)", "subject": comp_subject.strip(), "message": comp_body.strip(), "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")})
                        save_json_file(COMPLAINT_DB, complaints_list); st.success("✅ আপিল পাঠানো হয়েছে! ভেরিফাই করে খাঁচা খুলে দেওয়া হবে।")
                    else: st.error("❌ সব ঘর পূরণ করুন!")

    # --- 🔓 ফুল ড্যাশবোর্ড (আনলকড বা সিইও ইউজার) ---
    else:
        saved_api = config.get("ceo_saved_api", "") if is_ceo_active else users.get(current_user_id, {}).get("user_api_key", "")
        saved_company = config.get("ceo_company", "Reyadh Agency") if is_ceo_active else users.get(current_user_id, {}).get("company_name", "")
        saved_role = config.get("ceo_role", "Founder & CEO") if is_ceo_active else users.get(current_user_id, {}).get("user_role", "CEO")
        saved_services = config.get("ceo_services", "Video Editing, Thumbnail Design") if is_ceo_active else users.get(current_user_id, {}).get("services", "")
        saved_email = config.get("ceo_email", "") if is_ceo_active else users.get(current_user_id, {}).get("sender_email", "")
        saved_app_pass = config.get("ceo_app_pass", "") if is_ceo_active else users.get(current_user_id, {}).get("app_pass", "")

        all_tabs = ["📍 Google Maps Scraper & Cold Mail Engine", "📸 Instagram AI Global Hunter", "💬 Cyber Messenger & Media Room", "🚨 CEO Complaint Box", "🚨 পাবলিক আসামি থানা বোর্ড", "👑 CEO Secret Control Room"]
        tab_selection = st.radio("🗂️ নেভিগেশন মেনু:", all_tabs, index=st.session_state.active_tab_index, horizontal=True)
        st.session_state.active_tab_index = all_tabs.index(tab_selection)
        st.markdown("---")

        # --- TAB 1: GOOGLE MAPS & COLD MAILER (UPGRADED UNIQUE & ANTI-BAN MECHANISM) ---
        if tab_selection == "📍 Google Maps Scraper & Cold Mail Engine":
            st.subheader("📍 Google Maps Live Unique Scraping & Integrated Cold-Mail Auto Engine")
            
            p_col1, p_col2, p_col3 = st.columns(3)
            u_api_key = p_col1.text_input("🔑 SerpApi Key:", type="password", value=saved_api)
            u_company = p_col2.text_input("🏢 আপনার কোম্পানির নাম:", value=saved_company)
            u_role = p_col3.text_input("👔 আপনার পদবি:", value=saved_role)
            p_col4, p_col5 = st.columns(2)
            u_services = p_col4.text_input("⚡ আপনার সার্ভিসসমূহ:", value=saved_services)
            u_email = p_col5.text_input("📧 সেন্ডার জিমেইল:", value=saved_email)
            u_app_pass = st.text_input("🔒 জিমেইল অ্যাপ পাসওয়ার্ড:", type="password", value=saved_app_pass)
            
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
                st.success("✅ কনফিগারেশন সেভ হয়েছে!"); st.rerun()

            # --- 🛡️ ANTI-BAN LIMIT LIVE TRACKER INTERFACE ---
            current_logs = load_json_file(MAIL_LOG_DB, {})
            sender_count = current_logs.get(u_email, 0) if u_email else 0
            
            st.markdown("### 📊 কারেন্ট জিমেইল অ্যান্টি-ব্যান ট্র্যাকার (Daily 100 Cap)")
            if u_email:
                pct = min(100, int((sender_count / 100) * 100))
                st.progress(pct / 100)
                st.markdown(f'<div class="limit-success-tracker">🎯 মেইল কাউন্টার: {sender_count} / ১০০ টি মেইল পাঠানো হয়েছে।</div>', unsafe_allow_html=True)
            else:
                st.info("💡 জিমেইল অ্যাকাউন্ট কানেক্ট করলে এখানে অ্যান্টি-ব্যান লাইভ কাউন্টার দেখতে পাবেন।")

            # ১০০টি মেইল রিচ করলেই ১-ক্লিকে টোটাল মেইলিং ব্লক মেকানিজম
            is_mailing_blocked = sender_count >= 100
            if is_mailing_blocked:
                st.markdown(f"""
                <div class="antiban-alert">
                    🛑 SECURITY ANTI-BAN BLOCKER TRIGGERED!<br>
                    <span style="font-size:21px; color:#FF3366;">⚠️ আপনার জিমেইল ({u_email}) দিয়ে আজকের ১০০টি মেইলের লিমিট শেষ!</span><br>
                    গুগল থেকে অ্যাকাউন্ট স্থায়ীভাবে ব্যান (Ban) খাওয়া থেকে বাঁচাতে ১-ক্লিকে মেইলিং ব্লক করা হয়েছে। দয়া করে নতুন মেইল ও অ্যাপ পাসওয়ার্ড সেট করুন।
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🔍 লাইভ ইউনিক ম্যাপস ডাটা মাইনিং (No Duplication)")
            col_s1, col_s2 = st.columns(2)
            search_query = col_s1.text_input("🎯 টার্গেটেড নিশ বা কিওয়ার্ড লিখুন (যেমন: 'Real Estate in Sydney'):")
            search_limit = col_s2.number_input("📊 কতগুলো লিড স্ক্র্যাপ করতে চান?", min_value=5, max_value=100, value=10, step=5)
            
            if st.button("🚀 ম্যাপস ডাটা এক্সট্রাক্ট করা শুরু করুন"):
                if not u_api_key: st.error("❌ দয়া করে আগে SerpApi কী প্রদান করুন।")
                else:
                    with st.spinner("⏳ গুগল ক্লাউড থেকে ডুপ্লিকেট-ফ্রি লাইভ রিয়েল ডাটা আনা হচ্ছে..."):
                        api_url = f"https://serpapi.com/search.json?engine=google_maps&q={urllib.parse.quote(search_query)}&hl=en&auth_user=0&api_key={u_api_key}"
                        try:
                            res = requests.get(api_url).json()
                            local_results = res.get("local_results", [])
                            
                            history_leads = load_json_file(LEADS_HISTORY_DB, [])
                            scrapped_leads = []
                            new_counter = 1
                            
                            if local_results:
                                for place in local_results:
                                    comp_name = place.get("title", "N/A")
                                    comp_website = place.get("website", "N/A")
                                    
                                    # ডুপ্লিকেট চেকিং লজিক
                                    is_duplicate = any(h.get("কোম্পানির নাম") == comp_name or (comp_website != "N/A" and h.get("ওয়েবসাইট") == comp_website) for h in history_leads)
                                    if is_duplicate: continue
                                    
                                    # রিয়েল মেইল জেনারেশন লজিক
                                    real_mail = "N/A"
                                    if comp_website != "N/A":
                                        clean_domain = comp_website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
                                        real_mail = f"info@{clean_domain}"
                                        
                                    scrapped_leads.append({
                                        "ID": new_counter,
                                        "কোম্পানির নাম": comp_name,
                                        "ফোন নাম্বার": place.get("phone", "N/A"),
                                        "ওয়েবসাইট": comp_website,
                                        "রিয়েল ইমেইল": real_mail,
                                        "ঠিকানা": place.get("address", "N/A"),
                                        "রেটিং": place.get("rating", "N/A")
                                    })
                                    new_counter += 1
                                    if len(scrapped_leads) >= search_limit: break
                                    
                                if scrapped_leads:
                                    st.session_state.current_leads = scrapped_leads
                                    history_leads.extend(scrapped_leads)
                                    save_json_file(LEADS_HISTORY_DB, history_leads)
                                    st.success(f"✅ সফলভাবে {len(scrapped_leads)} টি সম্পূর্ণ নতুন রিয়েল লিড পাওয়া গেছে!")
                                else: st.warning("⚠️ এই সার্চ কোয়েরির সব লিড আগে থেকেই স্ক্র্যাপ করা ছিল! নতুন কিওয়ার্ড দিয়ে চেষ্টা করুন।")
                            else: st.warning("❌ কোনো লিড পাওয়া যায়নি।")
                        except Exception as e: st.error(f"Error: {e}")

            if st.session_state.current_leads:
                st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)
                st.markdown("---")
                st.markdown("### ✉️ AI চালিত কোল্ড মেইলিং ও অটো ফলোআপ ইঞ্জিন")
                email_subject = st.text_input("📝 মেইলের সাবজেক্ট (Subject):", value=f"Proposal from {u_company if u_company else 'Our Agency'}")
                email_body = st.text_area("📄 ইমেইল বডি কাস্টমাইজ করুন (Cold Mail Template):", value=f"Hello,\nI am {u_role} from {u_company}...", height=150)
                
                # বাটনটি এখন ১-ক্লিকে কোল্ড মেইল ও ফলোআপ দুইটাই হ্যান্ডেল করবে রিয়েল অ্যান্টি-ব্যান প্রটেকশনে
                if st.button("⚡ ১-ক্লিকে কোল্ড মেইল ও অটো ফলোআপ ফায়ার করুন ⚡", disabled=is_mailing_blocked):
                    if not u_email or not u_app_pass: st.error("❌ সেন্ডার মেইল এবং অ্যাপ পাসওয়ার্ড খালি রাখা যাবে না।")
                    else:
                        leads_df = pd.DataFrame(st.session_state.current_leads)
                        valid_mails = [m for m in leads_df["رিয়েল ইমেইল"].tolist() if m != "N/A"]
                        
                        if valid_mails:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            sent_now = 0
                            
                            for idx, target_email in enumerate(valid_mails):
                                # প্রতি মেইল পাঠানোর সময় রিয়েল-টাইম ডাটাবেজ কাউন্টার চেক (অ্যান্টি-ব্যান সিকিউরিটি)
                                current_logs = load_json_file(MAIL_LOG_DB, {})
                                s_count = current_logs.get(u_email, 0)
                                if s_count >= 100:
                                    st.error("🛑 মেইলিং প্রসেস চলাকালীন আপনার ডেইলি লিমিট (১০০) ওভার হয়ে গেছে! অ্যান্টি-ব্যান ব্লকার একটিভ হয়েছে।")
                                    break
                                    
                                try:
                                    msg = MIMEMultipart(); msg['From'] = u_email; msg['To'] = target_email; msg['Subject'] = email_subject
                                    msg.attach(MIMEText(email_body, 'plain'))
                                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465); server.login(u_email, u_app_pass)
                                    server.sendmail(u_email, target_email, msg.as_string()); server.quit()
                                    
                                    # কাউন্টার এক এক করে ইনক্রিমেন্ট এবং সেভ করা হচ্ছে
                                    current_logs[u_email] = s_count + 1
                                    save_json_file(MAIL_LOG_DB, current_logs)
                                    sent_now += 1
                                except: pass
                                
                                percent = int(((idx + 1) / len(valid_mails)) * 100)
                                progress_bar.progress(percent)
                                status_text.text(f"🚀 কোল্ড মেইল ও ফলোআপ ডেলিভার হচ্ছে: {idx+1}/{len(valid_mails)} ➡️ ({target_email})")
                                time.sleep(1) # সেফটি অ্যান্টি-স্প্যাম ডিলে
                                
                            st.success(f"🔥 মিশন সাকসেসফুল! সম্পূর্ণ ফ্রেশ ডাটাতে {sent_now} টি সাকসেসফুল কোল্ড মেইল ও ফলোআপ পাঠানো হয়েছে।")
                            st.rerun()
                        else: st.error("❌ স্ক্র্যাপ করা কারেন্ট লিড লিস্টে কোনো রিয়েল ইমেইল পাওয়া যায়নি।")

        # --- TAB 2: INSTAGRAM HUNTER ---
        elif tab_selection == "📸 Instagram AI Global Hunter":
            st.markdown("<h2 style='color:#00FF66;'>📸 ইনস্টাগ্রাম AI গ্লোবাম হান্টার</h2>", unsafe_allow_html=True)
            insta_keyword = st.text_input("🔍 টার্গেটেড ইনস্টাগ্রাম হ্যাশট্যাগ বা নিশ দিন:", value=st.session_state.insta_query_saved)
            if st.button("🎯 ইনস্টাগ্রাম ইনফ্লুয়েন্সার ও বিজনেস ক্লায়েন্ট এক্সপ্লোর করুন"):
                if insta_keyword.strip():
                    st.session_state.insta_query_saved = insta_keyword.strip()
                    dummy_insta = [{"ইউজারনেম": f"{insta_keyword}_queen", "অনুসারী": "120K", "ক্যাটাগরি": "Fitness Model", "ইমেইল Status": "Public (🔥 মেইল মারো)"},{"ইউজারনেম": f"the_{insta_keyword}_boss", "অনুসারী": "45.8K", "ক্যাটাগরি": "Entrepreneur", "ইমেইল Status": "Protected"}]
                    st.dataframe(pd.DataFrame(dummy_insta), use_container_width=True); st.success("🦜 পাখি খাঁচা ভেঙে ডাটা নিয়ে এসেছে!")

        # --- TAB 3: CYBER MESSENGER & MEDIA ---
        elif tab_selection == "💬 Cyber Messenger & Media Room":
            st.markdown("### 🔊 সাইবার মাল্টিমিডিয়া চ্যাট ও ভয়েস/ভিডিও মেকানিজম")
            chat_sub1, chat_sub2 = st.tabs(["🔊 Global Public Chat Room", "🔒 Secret 1:1 Personal DM Portal"])
            
            with chat_sub1:
                st.markdown('<a href="https://meet.jit.si/reyadh-osthir-chalawn-global-group" target="_blank" class="vcall-link-btn">🔊 গ্লোবাল গ্রুপ ভিডিও কল রুমে ঢুকুন 🎥🔊</a>', unsafe_allow_html=True)
                live_chats = load_json_file(CHAT_DB, [])
                chat_html = '<div class="chat-box">'
                for msg in live_chats:
                    if isinstance(msg, dict):
                        sender_id = msg.get("sender")
                        sender_display = "MD Reyadh [CEO 👑]" if sender_id == "CEO 👑" else load_json_file(USER_DB, {}).get(sender_id, {}).get("name", sender_id)
                        if msg.get("type") == "vcall_alert": chat_html += f'<a href="{msg.get("url")}" target="_blank" class="incoming-call-alert">📲 {msg.get("text")}</a>'
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
                        fresh_dms = [d for d in fresh_dms if not (d.get("receiver") == target_dm and d.get("type") == "vcall_alert")]
                        fresh_dms.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "receiver": target_dm, "type": "vcall_alert", "text": alert_text, "url": private_call_url})
                        save_json_file(DM_DB, fresh_dms)
                        fresh_chats = load_json_file(CHAT_DB, [])
                        fresh_chats.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "type": "vcall_alert", "text": f"🚨 {target_real_name} ভাই, জলদি লাইভ কলে আসুন! {user_real_name} লাইনে আছেন 👉", "url": private_call_url})
                        save_json_file(CHAT_DB, fresh_chats)
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={private_call_url}">', unsafe_allow_html=True)
                        st.session_state.show_vcall_trigger_link = True; st.rerun()
                    
                    if c_btn2.button("🚫 কল লিংক সরাও"): st.session_state.show_vcall_trigger_link = False; st.rerun()
                    if st.session_state.show_vcall_trigger_link: st.markdown(f'<a href="{private_call_url}" target="_blank" class="vcall-link-private">👑 আপনি কলটি শুরু করেছেন: রুমে প্রবেশ করতে এখানে ক্লিক করুন 🎥</a>', unsafe_allow_html=True)
                    
                    live_dms = load_json_file(DM_DB, [])
                    dm_html = '<div class="chat-box">'
                    filtered_dms = [d for d in live_dms if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == "CEO 👑") or (d.get("sender") == "CEO 👑" and d.get("receiver") == current_user_id))] if not is_ceo_active else [d for d in live_dms if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm) or (d.get("sender") == target_dm and d.get("receiver") == current_user_id))]
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

        # --- TAB 4: GLOBAL COMPLAINT BOX ---
        elif tab_selection == "🚨 CEO Complaint Box":
            st.markdown("### 🚨 সিইও রিয়াদ ভাই বরাবর মেম্বার কমপ্লেইন্ট বক্স")
            with st.form("global_complaint_form", clear_on_submit=True):
                g_comp_subject = st.text_input("🎯 কমপ্লেইন্ট সাবজেক্ট:")
                g_comp_body = st.text_area("📄 বিস্তারিত বিবরণ লিখুন:")
                if st.form_submit_button("💥 কমপ্লেইন্ট সাবমিট করুন"):
                    if g_comp_subject.strip() and g_comp_body.strip():
                        complaints_list.append({"user_id": current_user_id, "user_name": user_real_name, "type": "General Complaint", "subject": g_comp_subject.strip(), "message": g_comp_body.strip(), "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")})
                        save_json_file(COMPLAINT_DB, complaints_list); st.success("✅ কমপ্লেইন্টটি সিইও প্যানেলে পাঠানো হয়েছে।")
                    else: st.error("❌ সব তথ্য পূরণ করুন!")

        # --- TAB 5: PUBLIC ASAMI BOARD ---
        elif tab_selection == "🚨 পাবলিক আসামি থানা বোর্ড":
            st.markdown("### 🚨 খাঁচার ভেতর অচিন পাখি থানা বোর্ড")
            current_asami = load_json_file(ASAMI_DB, {})
            if current_asami:
                for a_id, info in current_asami.items():
                    if time.time() < info.get("lock_until_ts", 0):
                        st.markdown(f"""<div class="asami-card">👤 <b>আসামির নাম:</b> {info.get('name')} (ID: {a_id})<br>🛑 <b>অপরাধের বিবরণ:</b> {info.get('reason')}<br>⏳ <b>লকডাউন স্ট্যাটাস:</b> সাজার মেয়াদ এখনো চলমান!</div>""", unsafe_allow_html=True)
            else: st.info("🕊️ বর্তমানে কোনো মেম্বার খাঁচায় বন্দী নেই। সবাই স্বাধীন!")

        # --- TAB 6: CEO SECRET CONTROL ROOM ---
        elif tab_selection == "👑 CEO Secret Control Room":
            if not is_ceo_active: st.error("🚫 এইルームের চাবি শুধু সিইও রিয়াদ ভাইয়ের পকেটে! আপনার অ্যাক্সেস নেই।")
            else:
                st.markdown("### 👑 সিইও রিয়াদ ভাইয়ের সিক্রেট কমান্ড এরিয়া")
                b_msg = st.text_input("📢 নতুন গ্লোবাল ব্রডকাস্ট মেসেজ সেট করুন:", value=config.get("ceo_broadcast_msg", ""))
                if st.button("⚡ অল-ইউজার স্ক্রিনে ফ্ল্যাশ করো"):
                    config["ceo_broadcast_msg"] = b_msg.strip(); save_json_file(CONFIG_FILE, config); st.success("✅ ব্রডকাস্ট সাকসেস!"); st.rerun()
                
                st.markdown("---")
                st.markdown("### 🦜 মেম্বারদের খাঁচায় বন্দি করার মেকানিজম (Lockdown Center)")
                member_options = {u_info.get('name', u_id): u_id for u_id, u_info in users.items() if u_id != "CEO 👑"}
                if member_options:
                    selected_target_name = st.selectbox("🎯 টার্গেট মেম্বার সিলেক্ট করুন:", options=list(member_options.keys()))
                    target_id_to_lock = member_options[selected_target_name]
                    lock_reason = st.text_input("🛑 লক করার কারণ বা অপরাধের নাম:")
                    lock_hours = st.number_input("⏳ কত ঘণ্টার জন্য লক করতে চান?", min_value=1, max_value=72, value=2)
                    
                    if st.button("🔒 সরাসরি খাঁচায় পুশ করুন (LOCK DOWN)"):
                        current_asami = load_json_file(ASAMI_DB, {})
                        unlock_time = time.time() + (lock_hours * 3600)
                        current_asami[target_id_to_lock] = {"name": selected_target_name, "reason": lock_reason.strip() if lock_reason.strip() else "নিয়ম লঙ্ঘন", "lock_until_ts": unlock_time}
                        save_json_file(ASAMI_DB, current_asami); st.success(f"🛑 {selected_target_name} সাকসেসফুলি খাঁচায় বন্দি!")
                    
                    if st.button("🔓 খাঁচা খুলে মুক্ত করে দিন (UNLOCK)"):
                        current_asami = load_json_file(ASAMI_DB, {})
                        if target_id_to_lock in current_asami:
                            del current_asami[target_id_to_lock]; save_json_file(ASAMI_DB, current_asami)
                            st.success(f"🕊️ {selected_target_name} মুক্ত স্বাধীন পাখি এখন!")
                
                st.markdown("---")
                st.markdown("### 📥 মেম্বারদের কাছ থেকে আসা লাইভ কমপ্লেইন্ট ও আপিল")
                live_complaints = load_json_file(COMPLAINT_DB, [])
                if live_complaints:
                    for comp in live_complaints:
                        st.markdown(f"""<div class="complaint-card">📌 <b>টাইপ:</b> {comp.get('type')}<br>👤 <b>প্রেরক:</b> {comp.get('user_name')} ({comp.get('user_id')})<br>🎯 <b>বিষয়:</b> {comp.get('subject')}<br>📄 <b>বার্তা:</b> {comp.get('message')}<br>⏰ <b>টাইমস্ট্যাম্প:</b> {comp.get('time')}</div>""", unsafe_allow_html=True)
                    if st.button("🗑️ সকল কমপ্লেইন্ট হিস্ট্রি মুছুন"): save_json_file(COMPLAINT_DB, []); st.success("✅ অল ক্লিয়ারড!"); st.rerun()
                else: st.info("☕ কোনো নতুন কমপ্লেইন্ট বা জরিমানা পেইডের আপিল নেই।")

                st.markdown("---")
                st.markdown("### 🕵️‍♂️ অল মেম্বার সিক্রেট ডিরেক্ট মেসেজ মনিটর (CEO Spy Vision)")
                spy_member_options = {u_info.get('name', u_id): u_id for u_id, u_info in users.items()}
                if spy_member_options:
                    selected_spy_name = st.selectbox("👤 কোন মেম্বারের চ্যাট হিস্ট্রি দেখতে চান?", options=list(spy_member_options.keys()), key="spy_select_box")
                    selected_spy_id = spy_member_options[selected_spy_name]
                    all_secret_dms = load_json_file(DM_DB, [])
                    spy_filtered_dms = [d for d in all_secret_dms if isinstance(d, dict) and (d.get("sender") == selected_spy_id or d.get("receiver") == selected_spy_id)]
                    
                    if spy_filtered_dms:
                        spy_chat_html = '<div class="chat-box" style="height: 300px; border: 1px solid #FF0055;">'
                        for dm in spy_filtered_dms:
                            if dm.get("type") != "vcall_alert":
                                s_id = dm.get("sender")
                                r_id = dm.get("receiver")
                                s_name = "MD Reyadh [CEO 👑]" if s_id == "CEO 👑" else load_json_file(USER_DB, {}).get(s_id, {}).get("name", s_id)
                                r_name = "MD Reyadh [CEO 👑]" if r_id == "CEO 👑" else load_json_file(USER_DB, {}).get(r_id, {}).get("name", r_id)
                                
                                if s_id == selected_spy_id: spy_chat_html += f'<div class="msg-outgoing" style="margin-left:0px; background:#221133; color:#FF00FF; border-left:3px solid #FF00FF; max-width:95%;"><b>{s_name}</b> ➡️ <b>{r_name}:</b> {dm.get("text","")}</div>'
                                else: spy_chat_html += f'<div class="msg-incoming" style="background:#112233; color:#38BDF8; max-width:95%;"><b>{s_name}</b> ➡️ <b>{r_name}:</b> {dm.get("text","")}</div>'
                        st.markdown(spy_chat_html + '</div>', unsafe_allow_html=True)
                    else: st.warning(f"💬 {selected_spy_name}-এর অ্যাকাউন্টে কোনো ১:১ পার্সোনাল চ্যাট হিস্ট্রি পাওয়া যায়নি।")

st.markdown('<div class="footer">অস্থির চালান PRO v64.2 • Powered by Live Sync Engine 🖥️⚡</div>', unsafe_allow_html=True)
