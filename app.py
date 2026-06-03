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

users = st.session_state.users_cache
config = st.session_state.config_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
asami_list = st.session_state.asami_cache
mail_logs = st.session_state.mail_logs

st.set_page_config(page_title="অস্থির চালান PRO v58.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .ceo-alert { background: linear-gradient(90deg, #991B1B, #450A0A); border-left: 6px solid #EF4444; padding: 15px; border-radius: 8px; color: #FCA5A5; font-weight: bold; margin-bottom: 15px; font-family: 'Hind Siliguri', sans-serif; box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
    .lock-box { background: linear-gradient(90deg, #450A0A, #1A0505); border-left: 6px solid #EF4444; padding: 20px; border-radius: 8px; color: #FCA5A5; font-weight: bold; margin-bottom: 20px; }
    .asami-card { background: #111827; border: 1px solid #EF4444; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .chat-box { height: 350px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    
    /* 🎯 HTML VCALL LINK DESIGN */
    .vcall-link-btn { display: block !important; width: 100% !important; text-align: center !important; background: linear-gradient(90deg, #00FF66, #007A3D) !important; color: #000000 !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 20px !important; margin: 10px 0px 20px 0px !important; border-radius: 8px !important; text-decoration: none !important; border: none !important; box-shadow: 0 4px 15px rgba(0, 255, 102, 0.3); transition: 0.3s; }
    .vcall-link-btn:hover { transform: scale(1.01); background: linear-gradient(90deg, #00FF88, #00994D) !important; color: #000 !important; text-decoration: none !important; }
    
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "is_ceo" not in st.session_state: st.session_state.is_ceo = False
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "insta_query_saved" not in st.session_state: st.session_state.insta_query_saved = ""
if "active_dm_user" not in st.session_state: st.session_state.active_dm_user = None

# --- LIVE LOCKUP TRACKER & CHECKER ---
def check_user_lock(u_id):
    if u_id == "CEO 👑" or not u_id: return False, "", 0
    current_asami = load_json_file(ASAMI_DB, {})
    if u_id in current_asami:
        lock_until_ts = current_asami[u_id].get("lock_until_ts", 0)
        if time.time() < lock_until_ts:
            rem_sec = lock_until_ts - time.time()
            days = int(rem_sec // 86400)
            hours = int((rem_sec % 86400) // 3600)
            mins = int((rem_sec % 3600) // 60)
            secs = int(rem_sec % 60)
            
            if days > 0:
                time_str = f"{days} দিন {hours} ঘণ্টা {mins} মিনিট"
            else:
                time_str = f"{hours} ঘণ্টা {mins} মিনিট {secs} সেকেন্ড"
            return True, time_str, days
        else:
            if u_id in asami_list: del asami_list[u_id]; save_json_file(ASAMI_DB, asami_list)
    return False, "", 0

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v58.0 🖥️⚡</p>', unsafe_allow_html=True)
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
    
    saved_api = config.get("ceo_saved_api", "") if is_ceo_active else users.get(current_user_id, {}).get("user_api_key", "")
    saved_company = config.get("ceo_company", "Reyadh Agency") if is_ceo_active else users.get(current_user_id, {}).get("company_name", "")
    saved_role = config.get("ceo_role", "Founder & CEO") if is_ceo_active else users.get(current_user_id, {}).get("user_role", "CEO")
    saved_services = config.get("ceo_services", "Video Editing, Thumbnail Design") if is_ceo_active else users.get(current_user_id, {}).get("services", "")
    saved_email = config.get("ceo_email", "") if is_ceo_active else users.get(current_user_id, {}).get("sender_email", "")
    saved_app_pass = config.get("ceo_app_pass", "") if is_ceo_active else users.get(current_user_id, {}).get("app_pass", "")

    # --- 🚨 LIVE SYSTEM SYNC GLOBAL BANNER ---
    fresh_config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    if fresh_config.get("ceo_broadcast_msg", ""):
        st.markdown(f"""
        <div class="ceo-alert">
            👑 <b>সিইও রিয়াদ ভাইয়ের আদেশ:</b> {fresh_config.get("ceo_broadcast_msg", "")}
        </div>
        """, unsafe_allow_html=True)

    if is_ceo_active: st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    is_current_user_locked, remaining_lock_time, total_days_locked = check_user_lock(current_user_id)

    # ক্যাটাগরি ট্যাব
    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5 = st.tabs([
        "📍 Google Maps Scraper & Cold Mail Engine", 
        "📸 Instagram AI Global Hunter", 
        "💬 Cyber Messenger & Media Room",
        "🚨 পাবলিক আসামি থানা বোর্ড",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1: GOOGLE MAPS ---
    with engine_tab1:
        st.subheader("📍 Google Maps Live Scraping & Integrated Cold Mailer")
        if is_current_user_locked:
            st.markdown(f"""
            <div class="lock-box" style="text-align:center;">
                🛑 <b>অ্যাক্সেস ব্লকড! আপনি এখন সাইবার থানার কয়েদি!</b><br><br>
                ⏳ আপনার বাকি সাজার মেয়াদ: <span style="color:#00FF66;"><b>{remaining_lock_time}</b></span>
            </div>
            """, unsafe_allow_html=True)
        else:
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
                st.success("✅ কনফিগারেশন সেভ হয়েছে!")
                time.sleep(0.5); st.rerun()

            st.markdown("---")
            st.markdown("### 🔍 লাইভ ডাটা স্ক্র্যাপিং রাডার")
            sc_col1, sc_col2 = st.columns(2)
            search_query = sc_col1.text_input("গুগল ম্যাপস সার্চ কিওয়ার্ড (যেমন: Gym in New York):")
            max_results = sc_col2.number_input("সর্বোচ্চ লিড সংখ্যা:", min_value=1, max_value=100, value=10)
            
            if st.button("📍 লাইভ স্ক্র্যাপার run করুন ⚡") and search_query.strip() and saved_api:
                with st.spinner("ডাটা এক্সট্র্যাক্ট হচ্ছে..."):
                    res = requests.get("https://serpapi.com/search.json", params={"engine": "google_maps", "q": search_query.strip(), "api_key": saved_api, "num": int(max_results)})
                    if res.status_code == 200:
                        local_results = res.json().get("local_results", [])
                        leads_list = []
                        for item in local_results:
                            title = item.get("title", "Business Owner")
                            website = item.get("website", "None")
                            clean_domain = website.replace("https://", "").replace("http://", "").replace("www.", "") if website else ""
                            raw_domain = clean_domain.split("/")[0] if clean_domain else ""
                            combined_emails = f"info@{raw_domain}, hello@{raw_domain}, contact@{raw_domain}" if raw_domain else "None"
                            leads_list.append({"Name": title, "Email": combined_emails, "Website": website, "Phone": item.get("phone", "None")})
                        st.session_state.current_leads = leads_list
                        st.success(f"✅ সফলভাবে {len(leads_list)}টি লিড মেমোরিতে লোড হয়েছে!")
            
            if st.session_state.current_leads:
                st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)

    # --- TAB 2: INSTAGRAM HUNTER ---
    with engine_tab2:
        st.markdown("<h2 style='color:#00FF66;'>📸 ইনস্টাগ্রাম AI গ্লোবাল হান্টার</h2>", unsafe_allow_html=True)
        if is_current_user_locked: st.markdown(f'<div class="lock-box">🛑 সাজাপ্রাপ্ত আসামিদের জন্য রাডার সম্পূর্ণ ব্লকড!</div>', unsafe_allow_html=True)
        else:
            target_category = st.selectbox("🎯 ক্লায়েন্ট ক্যাটাগরি:", options=["Real Estate Agents", "Fitness Coaches", "E-commerce Brands"])
            if st.button("🚀 গ্লোবাল হান্টিং রাডার অ্যাক্টিভেট করুন"):
                st.session_state.insta_query_saved = target_category
            if st.session_state.insta_query_saved:
                final_google_query = f'site:instagram.com "{st.session_state.insta_query_saved}"'
                st.markdown(f'<a href="https://www.google.com/search?q={urllib.parse.quote(final_google_query)}" target="_blank"><button style="background-color:#4285F4; color:white; padding:12px; border:none; border-radius:8px; width:100%; cursor:pointer; font-weight:bold;">🎯 গুগল এক্স-রে ফিল্টারে হান্ট করুন</button></a>', unsafe_allow_html=True)

    # --- TAB 3: CYBER MESSENGER (🎯 AUTOMATIC CALL ALERT DISPATCHER) ---
    with engine_tab3:
        st.markdown("### 🔊 সাইবার মাল্টিমিডিয়া চ্যাট ও ভয়েস/ভিডিও মেকানিজম")
        
        chat_sub1, chat_sub2 = st.tabs(["🔊 Global Public Chat Room", "🔒 Secret 1:1 Personal DM Portal"])
        
        @st.fragment(run_every=1)
        def render_live_public_chat():
            live_chats = load_json_file(CHAT_DB, [])
            st.markdown('<a href="https://meet.jit.si/reyadh-osthir-chalawn-global-group" target="_blank" class="vcall-link-btn">🔊 গ্লোবাল গ্রুপ ভিডিও কল রুমে ঢুকুন 🎥🔊</a>', unsafe_allow_html=True)
            
            chat_html = '<div class="chat-box">'
            for msg in live_chats:
                if not isinstance(msg, dict): continue
                sender_id = msg.get("sender")
                sender_display = "MD Reyadh [CEO 👑]" if sender_id == "CEO 👑" else load_json_file(USER_DB, {}).get(sender_id, {}).get("name", sender_id)
                msg_class = "msg-outgoing" if sender_id == current_user_id else "msg-incoming"
                chat_html += f'<div class="{msg_class}"><b>{sender_display}:</b> {msg.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{msg.get("time","")}</small></div>'
            st.markdown(chat_html + '</div>', unsafe_allow_html=True)

        with chat_sub1:
            render_live_public_chat()
            with st.form("pub_text_v58", clear_on_submit=True):
                t_msg = st.text_input("📝 টেক্সট মেসেজ লিখুন:")
                if st.form_submit_button("পাঠান ✉️") and t_msg.strip():
                    fresh_chats = load_json_file(CHAT_DB, [])
                    fresh_chats.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "type": "text", "text": t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                    save_json_file(CHAT_DB, fresh_chats)
                    st.rerun()
        
        with chat_sub2:
            all_users_list = [u for u in users.keys() if u != current_user_id and u != "CEO 👑"]
            if is_ceo_active: all_users_list = list(users.keys())
                
            if all_users_list:
                default_index = all_users_list.index(st.session_state.active_dm_user) if st.session_state.active_dm_user in all_users_list else 0
                target_dm = st.selectbox("🔒 মেম্বার সিলেক্ট করুন:", options=all_users_list, index=default_index, key="dm_select_v58")
                
                if target_dm:
                    st.session_state.active_dm_user = target_dm
                    sorted_pair = sorted([str(current_user_id), str(target_dm)])
                    private_call_url = f"https://meet.jit.si/reyadh-private-1to1-{sorted_pair[0]}-{sorted_pair[1]}"
                    
                    # 🎯 ম্যাজিক বাটন: ক্লিক করলেই অটোমেটিক মেসেজ যাবে এবং কল ওপেন হবে!
                    if st.button(f"📞 {users.get(target_dm, {}).get('name', target_dm)} কে সরাসরি ভিডিও কল দিন (অটো-অ্যালার্টসহ) 🎥", use_container_width=True):
                        # ১. ব্যাকগ্রাউন্ডে ইনবক্সে রিয়েল-টাইম নোটিফিকেশন মেসেজ পুশ
                        fresh_dms = load_json_file(DM_DB, [])
                        alert_text = f"🚨 কলার অ্যালার্ট: {user_real_name} আপনাকে ভিডিও কলে ডাকছেন! জলদি চ্যাটবক্সের উপরের লিঙ্কে ক্লিক করে জয়েন হোন! 📲"
                        fresh_dms.append({
                            "sender": "CEO 👑" if is_ceo_active else current_user_id, 
                            "receiver": target_dm, 
                            "type": "text", 
                            "text": alert_text, 
                            "time": datetime.datetime.now().strftime("%I:%M %p")
                        })
                        save_json_file(DM_DB, fresh_dms)
                        
                        # ২. জাভাস্ক্রিপ্ট ইনজেকশন দিয়ে কোনো রিফ্রেশ ছাড়াই ইনস্ট্যান্ট নতুন ট্যাবে কল ওপেন
                        js_trigger = f"""
                        <script>
                            window.open("{private_call_url}", "_blank");
                        </script>
                        """
                        st.components.v1.html(js_trigger, height=0)
                        st.success("🚀 নোটিফিকেশন পাঠানো হয়েছে এবং কল উইন্ডো ওপেন হয়েছে!")
                    
                    st.markdown(f"#### 💬 {users.get(target_dm, {}).get('name', target_dm)}-এর সাথে গোপন মেসেজ বক্স")
                    
                    @st.fragment(run_every=1)
                    def render_live_dm_box(t_user):
                        live_dms = load_json_file(DM_DB, [])
                        dm_html = '<div class="chat-box">'
                        filtered_dms = [d for d in live_dms if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == t_user) or (d.get("sender") == t_user and d.get("receiver") == current_user_id))]
                        if filtered_dms:
                            for dm in filtered_dms:
                                dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else load_json_file(USER_DB, {}).get(dm.get("sender"), {}).get("name", dm.get("sender"))
                                dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                                dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{dm.get("time","")}</small></div>'
                        else:
                            dm_html += '<div style="color:#64748B; text-align:center; padding-top:150px;">কোনো মেসেজ নেই।</div>'
                        dm_html += '</div>'
                        st.markdown(dm_html, unsafe_allow_html=True)

                    render_live_dm_box(target_dm)
                    
                    with st.form("dm_text_v58", clear_on_submit=True):
                        t_dm = st.text_input(f"✉️ {users.get(target_dm, {}).get('name', target_dm)}-কে টেক্সট পাঠান:")
                        if st.form_submit_button("মেসেজ পাঠান 🚀"):
                            if t_dm.strip():
                                fresh_dms = load_json_file(DM_DB, [])
                                fresh_dms.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "receiver": target_dm, "type": "text", "text": t_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                                save_json_file(DM_DB, fresh_dms)
                                st.rerun()

    # --- TAB 4: PUBLIC ASAMI BOARD ---
    with engine_tab4:
        st.markdown("<h2 style='color:#EF4444;'>🚨 সাইবার থানা আসামি বোর্ড 🚓</h2>", unsafe_allow_html=True)
        @st.fragment(run_every=2)
        def render_live_asami_board():
            current_asami = load_json_file(ASAMI_DB, {})
            if current_asami:
                for a_id, a_info in list(current_asami.items()):
                    is_l, rem_t_str, _ = check_user_lock(a_id)
                    if is_l:
                        st.markdown(f"""
                        <div class="asami-card">
                            <h4 style="color:#FFF;">👤 আসামি: {load_json_file(USER_DB, {}).get(a_id, {}).get('name', a_id)}</h4>
                            <p style="color:#FFAAAA;">❌ <b>অপরাধ:</b> {a_info.get('crime')}</p>
                            <p style="color:#38BDF8;">⏳ <b>মুক্তির বাকি:</b> <b style="color:#00FF66;">{rem_t_str}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
            else: st.info("🕊️ ড্যাশবোর্ডে এখন কোনো আসামি নেই!")
        render_live_asami_board()

    # --- TAB 5: CEO SECRET CONTROL ROOM ---
    with engine_tab5:
        st.subheader("👑 Riad Bhai's Secret Control Room")
        if is_ceo_active:
            st.success("🔓 ফুল সিইও কন্ট্রোল অ্যাক্টিভেটেড!")
            u_broadcast_msg = st.text_area("মেম্বারদের জন্য নতুন নোটিশ/আদেশ লিখুন:", value=config.get("ceo_broadcast_msg", ""))
            if st.button("🚀 গ্লোবাল এলার্ট জারি করুন"):
                config["ceo_broadcast_msg"] = u_broadcast_msg.strip()
                save_json_file(CONFIG_FILE, config); st.success("🔥 নোটিফিকেশন লাইভ করা হয়েছে!"); time.sleep(0.3); st.rerun()
        else: st.error("🔒 এই সেকশনটি শুধুমাত্র মেইন সিইও প্যানেল দিয়ে এক্সেস করা যাবে।")

    # --- 🔄 WHOLE PAGE HIGH-SPEED SYNC ENGINE ---
    @st.fragment(run_every=2)
    def global_heartbeat_loop():
        pass
    global_heartbeat_loop()

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v58.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
