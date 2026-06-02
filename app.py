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
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- MULTI-USER SECURE STORAGE LAYER ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
CHAT_DB = "system_chat_memory.json"
DM_DB = "system_dm_memory.json"
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
if "chat_cache" not in st.session_state: st.session_state.chat_cache = load_json_file(CHAT_DB, [])
if "dm_cache" not in st.session_state: st.session_state.dm_cache = load_json_file(DM_DB, [])
if "asami_cache" not in st.session_state: st.session_state.asami_cache = load_json_file(ASAMI_DB, {})

users = st.session_state.users_cache
config = st.session_state.config_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
asami_list = st.session_state.asami_cache

st.set_page_config(page_title="অস্থির চালান PRO v47.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .lock-box { background: linear-gradient(90deg, #450A0A, #1A0505); border-left: 6px solid #EF4444; padding: 20px; border-radius: 8px; color: #FCA5A5; font-weight: bold; margin-bottom: 20px; }
    .limit-box { background: linear-gradient(90deg, #7C2D12, #451A03); border: 2px solid #EA580C; padding: 20px; border-radius: 8px; color: #FFEDD5; font-size: 18px; font-weight: bold; margin-top: 15px; text-align: center; }
    .chat-box { height: 400px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    .vcall-btn-group { background: linear-gradient(90deg, #00FF66, #007A3D) !important; color: black !important; font-weight: bold !important; border-radius: 8px !important; text-align: center; padding: 10px; text-decoration: none; display: inline-block; width: 100%; margin-bottom: 15px; }
    .vcall-btn-private { background: linear-gradient(90deg, #FF007F, #7928CA) !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; text-align: center; padding: 10px; text-decoration: none; display: inline-block; width: 100%; margin-bottom: 15px; }
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
        if time.time() < lock_until_ts:
            rem = lock_until_ts - time.time()
            return True, f"{int(rem // 60)} মিনিট"
        else:
            del asami_list[u_id]; save_json_file(ASAMI_DB, asami_list)
    return False, ""

# --- LOGIN GATEWAY ---
if st.session_state.logged_in_user is None and not st.session_state.is_ceo:
    st.markdown('<p class="main-title">অস্থির চালান PRO v47.0 🖥️⚡</p>', unsafe_allow_html=True)
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
                    users[reg_id.strip()] = {"name": reg_name.strip(), "badge": "None", "user_api_key": "", "company_name": "", "services": "", "sender_email": "", "app_pass": "", "last_seen": time.time()}
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
    
    if is_ceo_active: st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    is_current_user_locked, remaining_lock_time = check_user_lock(current_user_id)

    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5 = st.tabs([
        "📍 Google Maps Scraper & Fixed Mail Engine", 
        "📸 Instagram AI Global Hunter", 
        "💬 Cyber Messenger & Media Room",
        "🚨 পাবলিক আসামি থানা বোর্ড",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1: GOOGLE MAPS & Fixed 100 LIMIT COLD MAIL ENGINE ---
    with engine_tab1:
        st.subheader("📍 Google Maps Live Scraping & Bulletproof Cold Mailer")
        if is_current_user_locked:
            st.markdown(f'<div class="lock-box">❌ অ্যাক্সেস ডিনাইড! সিইও রিয়াদ ভাই লক করেছেন। সাজার মেয়াদ আরও {remaining_lock_time} বাকি!</div>', unsafe_allow_html=True)
        else:
            # --- PROFILE & SECURITY SETTINGS STORAGE ---
            st.markdown("### ⚙️ ইউজার প্রোফাইল ও সিকিউরিটি কনফিগারেশন (একবার সেভ করলেই স্থায়ী থাকবে)")
            
            # লোড ডাটাবেজ ভ্যালু
            saved_api = config.get("ceo_saved_api", "") if is_ceo_active else users.get(current_user_id, {}).get("user_api_key", "")
            saved_company = config.get("ceo_company", "Reyadh Agency") if is_ceo_active else users.get(current_user_id, {}).get("company_name", "")
            saved_services = config.get("ceo_services", "Video Editing, Thumbnail Design") if is_ceo_active else users.get(current_user_id, {}).get("services", "")
            saved_email = config.get("ceo_email", "") if is_ceo_active else users.get(current_user_id, {}).get("sender_email", "")
            saved_app_pass = config.get("ceo_app_pass", "") if is_ceo_active else users.get(current_user_id, {}).get("app_pass", "")

            p_col1, p_col2, p_col3 = st.columns(3)
            u_api_key = p_col1.text_input("🔑 SerpApi Key:", type="password", value=saved_api)
            u_company = p_col2.text_input("🏢 আপনার কোম্পানির নাম:", value=saved_company)
            u_services = p_col3.text_input("⚡ আপনার সার্ভিসসমূহ (কমা দিয়ে লিখুন):", value=saved_services)
            
            p_col4, p_col5 = st.columns(2)
            u_email = p_col4.text_input("📧 সেন্ডার জিমেইল (Gmail SMTP):", value=saved_email)
            u_app_pass = p_col5.text_input("🔒 জিমেইল অ্যাপ পাসওয়ার্ড (App Password):", type="password", value=saved_app_pass)
            
            if st.button("💾 প্রোফাইল ও সিকিউরিটি ডাটা পার্মানেন্ট সেভ করুন"):
                if is_ceo_active:
                    config["ceo_saved_api"] = u_api_key.strip(); config["ceo_company"] = u_company.strip()
                    config["ceo_services"] = u_services.strip(); config["ceo_email"] = u_email.strip()
                    config["ceo_app_pass"] = u_app_pass.strip(); save_json_file(CONFIG_FILE, config)
                else:
                    users[current_user_id]["user_api_key"] = u_api_key.strip(); users[current_user_id]["company_name"] = u_company.strip()
                    users[current_user_id]["services"] = u_services.strip(); users[current_user_id]["sender_email"] = u_email.strip()
                    users[current_user_id]["app_pass"] = u_app_pass.strip(); save_json_file(USER_DB, users)
                st.success("✅ সমস্ত কনফিগারেশন এবং সিকিউরিটি ডাটাবেজে লক করা হয়েছে!")
                time.sleep(0.5); st.rerun()

            st.markdown("---")
            st.markdown("### 🔍 লাইভ ডাটা স্ক্র্যাপিং রাডার")
            sc_col1, sc_col2 = st.columns(2)
            search_query = sc_col1.text_input("গুগল ম্যাপস সার্চ কিওয়ার্ড (যেমন: Gym in New York, Dentist in Miami):")
            max_results = sc_col2.number_input("সর্বোচ্চ লিড সংখ্যা (অটো সিকিউরড):", min_value=1, max_value=100, value=10)
            
            if st.button("📍 লাইভ স্ক্র্যাপার রান করুন ⚡") and search_query.strip() and saved_api:
                with st.spinner("গুগল ম্যাপস থেকে লাইভ কাস্টমার ডাটাবেজ এক্সট্র্যাক্ট হচ্ছে..."):
                    res = requests.get("https://serpapi.com/search.json", params={"engine": "google_maps", "q": search_query.strip(), "api_key": saved_api, "num": int(max_results)})
                    if res.status_code == 200:
                        local_results = res.json().get("local_results", [])
                        leads_list = []
                        for item in local_results:
                            title = item.get("title", "Business Owner")
                            website = item.get("website", "None")
                            clean_domain = website.replace("https://", "").replace("http://", "").replace("www.", "") if website else ""
                            raw_domain = clean_domain.split("/")[0] if clean_domain else ""
                            generated_email = f"info@{raw_domain}" if raw_domain else "None"
                            leads_list.append({"Name": title, "Email": generated_email, "Website": website, "Phone": item.get("phone", "None")})
                        st.session_state.current_leads = leads_list
                        st.success(f"✅ সফলভাবে {len(leads_list)}টি কাস্টমার লিড মেমোরিতে লোড হয়েছে!")
            
            if st.session_state.current_leads:
                st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)
                
                # --- AUTO FIXED 100 LIMIT COLD EMAIL ENGINE ---
                st.markdown("---")
                st.markdown("### 🚀 ওয়ান-ক্লিক অ্যাডভান্সড অ্যান্টি-ব্যান কোল্ড মেইল থ্রাস্টার")
                
                # স্পিচ বা টেমপ্লেট কাস্টমাইজেশন বক্স
                mail_speech = st.text_area("📝 কোল্ড মেইল স্পিচ/টেমপ্লেট (অটো ক্লায়েন্ট নাম ও কোম্পানি রিপ্লেস হবে):", 
                                           value="Hello {Client Name},\n\nI was reviewing your business profile at {Business Name} and noticed some huge scaling opportunities.\nWe specialize in {Your Services} and can help your company grow instantly.\n\nLet me know your thoughts.\n\nBest Regards,\n{Sender Name}\n{Sender Company}")

                if st.button("🔥 ১-ক্লিকে ১০০ ক্লায়েন্টকে অটো-মেইল ফায়ার করুন"):
                    if not saved_email or not saved_app_pass:
                        st.error("❌ প্রোফাইল সেকশনে গিয়ে আগে আপনার মেইল এবং অ্যাপ পাসওয়ার্ড সেভ করুন!")
                    else:
                        try:
                            server = smtplib.SMTP("smtp.gmail.com", 587)
                            server.starttls()
                            server.login(saved_email.strip(), saved_app_pass.strip())
                            
                            sent_count = 0
                            limit_reached = False
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for idx, lead in enumerate(st.session_state.current_leads):
                                # ডেইলি মেইল লিমিট চেক
                                if sent_count >= 100:
                                    limit_reached = True
                                    break
                                    
                                target_mail = lead.get('Email', 'None')
                                if target_mail == "None" or "@" not in target_mail:
                                    continue
                                
                                # ডাইনামিক ক্লায়েন্ট স্পিচ জেনারেশন লজিক
                                custom_body = mail_speech.replace("{Client Name}", lead.get('Name', 'Business Owner'))\
                                                         .replace("{Business Name}", lead.get('Name', 'Your Business'))\
                                                         .replace("{Your Services}", saved_services)\
                                                         .replace("{Sender Name}", user_real_name)\
                                                         .replace("{Sender Company}", saved_company)
                                
                                msg = MIMEMultipart()
                                msg['From'] = saved_email.strip()
                                msg['To'] = target_mail.strip()
                                msg['Subject'] = f"Strategic Expansion Proposal for {lead.get('Name')}"
                                msg.attach(MIMEText(custom_body, 'plain'))
                                
                                server.sendmail(saved_email.strip(), target_mail.strip(), msg.as_string())
                                sent_count += 1
                                
                                # প্রোগ্রেস বার আপডেট
                                progress_bar.progress((idx + 1) / len(st.session_state.current_leads))
                                status_text.text(f"🚀 মেইল পাঠানো হচ্ছে: {sent_count}/{len(st.session_state.current_leads)} (টার্গেট: {target_mail})")
                                
                                # 🔥 ANTI-BAN SECURITY DELAY: ৩ থেকে ৭ সেকেন্ডের র্যান্ডম ডিলে যাতে গুগল স্প্যাম না ধরে
                                time.sleep(random.randint(3, 7))
                                
                            server.quit()
                            
                            if limit_reached:
                                st.markdown("""
                                <div class="limit-box">
                                    🚨 ভাই, আজকের ১০০ মেইল লিমিট শেষ! ব্যান খাওয়া থেকে বাঁচতে ইমেইল সেকশনে গিয়ে নতুন জিমেইল ও অ্যাপ পাসওয়ার্ড অ্যাড করো। খামতির কোনো জায়গা নাই!
                                </div>
                                """, unsafe_allow_html=True)
                            
                            if sent_count > 0:
                                st.success(f"🔥 মিশন সাকসেস! অ্যান্টি-ব্যান সিকিউরিটিসহ সফলভাবে {sent_count}টি ক্লায়েন্টের ইনবক্সে আলাদা আলাদা স্পিচসহ মেইল ফায়ার করা হয়েছে!")
                        except Exception as e:
                            st.error(f"❌ SMTP কানেকশন বা সিকিউরিটি ফেল করেছে: {str(e)}")

    # --- TAB 2: INSTAGRAM HUNTER WITH TOP COUNTRIES ---
    with engine_tab2:
        st.markdown("<h2 style='color:#00FF66;'>📸 ইনস্টাগ্রাম AI গ্লোবাল হান্টার</h2>", unsafe_allow_html=True)
        
        target_category = st.selectbox("🎯 ক্লায়েন্ট ক্যাটাগরি সিলেক্ট করুন:", options=["Real Estate Agents", "Fitness Coaches", "E-commerce Brands", "Custom Category"])
        inst_query = st.text_input("🔍 কাস্টম ক্যাটাগরি নাম লিখুন:") if target_category == "Custom Category" else target_category
        
        # 🌍 TOP COUNTRY SELECTOR ADDED
        country_mode = st.selectbox("🌍 টার্গেটেড কান্ট্রি ফিল্টার করুন:", options=["United States (USA)", "United Kingdom (UK)", "Canada", "Australia", "Custom Country"])
        final_country = st.text_input("✍️ কাস্টম দেশের নাম বা রিজিয়ন লিখুন:") if country_mode == "Custom Country" else country_mode

        if st.button("🚀 গ্লোবাল হান্টিং রাডার অ্যাক্টিভেট করুন") and inst_query.strip():
            st.session_state.insta_query_saved = f"{inst_query.strip()} in {final_country}"
            
        if st.session_state.insta_query_saved:
            final_google_query = f'site:instagram.com "{st.session_state.insta_query_saved}"'
            st.markdown(f'<a href="https://www.google.com/search?q={urllib.parse.quote(final_google_query)}" target="_blank"><button style="background-color:#4285F4; color:white; padding:12px; border:none; border-radius:8px; width:100%; cursor:pointer; font-weight:bold;">🎯 গুগল এক্স-রে ফিল্টারে {st.session_state.insta_query_saved} হান্ট করুন</button></a>', unsafe_allow_html=True)

    # --- TAB 3: CYBER MESSENGER & MEDIA ROOM ---
    with engine_tab3:
        st.markdown("### 🔊 সাইবার মাল্টিমিডিয়া চ্যাট ও ভয়েস/ভিডিও মেকানিজম")
        chat_sub1, chat_sub2 = st.tabs(["🔊 Global Public Chat Room (গ্রুপ চ্যাট)", "🔒 Secret 1:1 Personal DM Portal (গোপন ইনবক্স)"])
        
        with chat_sub1:
            st.markdown("#### 👥 গ্লোবাল গ্রুপ ভিডিও কল (সবাই একসাথে যোগ দিন)")
            st.markdown('<a href="https://meet.jit.si/reyadh-osthir-chalawn-global-group" target="_blank" class="vcall-btn-group">🔊 গ্রুপ ভিডিও কল রুমে ঢুকুন (সবাই একসাথে ক্যাচাল পাড়ুন) 🎥🔊</a>', unsafe_allow_html=True)
            
            col_chat, col_members = st.columns([4, 1.5])
            with col_chat:
                chat_html = '<div class="chat-box">'
                for msg in chat_messages:
                    if not isinstance(msg, dict): continue
                    sender_id = msg.get("sender")
                    sender_display = "MD Reyadh [CEO 👑]" if sender_id == "CEO 👑" else users.get(sender_id, {}).get("name", sender_id)
                    msg_class = "msg-outgoing" if sender_id == current_user_id else "msg-incoming"
                    chat_html += f'<div class="{msg_class}"><b>{sender_display}:</b> {msg.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{msg.get("time","")}</small></div>'
                st.markdown(chat_html + '</div>', unsafe_allow_html=True)
                
                with st.form("pub_text_v47", clear_on_submit=True):
                    t_msg = st.text_input("📝 টেক্সট মেসেজ লিখুন:")
                    if st.form_submit_button("পাঠান ✉️") and t_msg.strip():
                        chat_messages.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "type": "text", "text": t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                        save_json_file(CHAT_DB, chat_messages); st.rerun()
            
            with col_members:
                st.markdown("### 👥 একটিভ মেম্বার্স")
                for u_id, u_data in users.items():
                    if u_id != current_user_id:
                        asami_tag = " 🚨" if u_id in asami_list else ""
                        if st.button(f"💬 {u_data.get('name')}{asami_tag}", key=f"quick_dm_{u_id}"):
                            st.session_state.active_dm_user = u_id; st.rerun()
        
        with chat_sub2:
            st.markdown("#### 🔒 ওয়ান-টু-ওয়ান সিক্রেট ইনবক্স ও প্রাইভেট ট্রাইব্যুনাল")
            all_users_list = [u for u in users.keys() if u != current_user_id]
            default_index = all_users_list.index(st.session_state.active_dm_user) if st.session_state.active_dm_user in all_users_list else 0
            
            if all_users_list:
                target_dm = st.selectbox("যার সাথে ওয়ান-টু-ওয়ান চ্যাট/কল করবেন তাকে সিলেক্ট করুন:", options=all_users_list, index=default_index)
                if target_dm:
                    st.session_state.active_dm_user = target_dm
                    sorted_pair = sorted([str(current_user_id), str(target_dm)])
                    private_call_url = f"https://meet.jit.si/reyadh-private-1to1-{sorted_pair[0]}-{sorted_pair[1]}"
                    
                    target_display_name = "আসামি" if target_dm in asami_list else users.get(target_dm, {}).get("name", target_dm)
                    st.markdown(f'<a href="{private_call_url}" target="_blank" class="vcall-btn-private">🔒 {target_display_name}-এর সাথে ১:১ প্রাইভেট ভিডিও কল (একলা সাইজ করুন) 🔒🎥</a>', unsafe_allow_html=True)
                    
                    dm_html = '<div class="chat-box">'
                    filtered_dms = [d for d in dm_messages if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm) or (d.get("sender") == target_dm and d.get("receiver") == current_user_id))]
                    for dm in filtered_dms:
                        dm_sender_name = "MD Reyadh [CEO 👑]" if dm.get("sender") == "CEO 👑" else users.get(dm.get("sender"), {}).get("name", dm.get("sender"))
                        dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                        dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{dm.get("time","")}</small></div>'
                    st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                    
                    with st.form("dm_text_v47", clear_on_submit=True):
                        t_dm = st.text_input("گوبن মেসেজ লিখুন:")
                        if st.form_submit_button("ডিএম পাঠান 🔐") and t_dm.strip():
                            dm_messages.append({"sender": "CEO 👑" if is_ceo_active else current_user_id, "receiver": target_dm, "type": "text", "text": t_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                            save_json_file(DM_DB, dm_messages); st.rerun()

    # --- TAB 4: PUBLIC ASAMI BOARD ---
    with engine_tab4:
        st.markdown("<h2 style='color:#EF4444;'>🚨 অস্থির চালান - সাইবার থানা আসামি বোর্ড 🚓</h2>", unsafe_allow_html=True)
        if asami_list:
            for a_id, a_info in list(asami_list.items()):
                check_user_lock(a_id)
                st.markdown(f"""
                <div class="asami-card">
                    <h4>👤 আসামি: {users.get(a_id, {}).get('name', a_id)} (ID: {a_id})</h4>
                    <p style="margin:2px 0;">❌ <b>অপরাধের বিবরণ:</b> <span style="color:#FFF; font-weight:bold;">{a_info.get('crime')}</span></p>
                    <p style="margin:2px 0; color:#FCA5A5;">⏳ <b>সাজার মেয়াদ:</b> <span style="color:#FF0000; font-weight:bold;">{a_info.get('duration')} দিন</span></p>
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
                    target_suspect = st.selectbox("কাকে আসামি বানাবেন?", options=all_users_avail, key="suspect_box_v47")
                    crime_note = st.text_input("অপরাধ বা ট্রোলের কারণ লিখুন:")
                    lock_days = st.number_input("🔒 কতদিনের জন্য স্ক্র্যাপার লক করবেন? (Days):", min_value=1, max_value=30, value=2)
                    if st.button("🔨 রায় ঘোষণা করুন", use_container_width=True):
                        if crime_note.strip():
                            asami_list[target_suspect] = {"crime": crime_note.strip(), "duration": str(lock_days), "lock_until_ts": time.time() + (int(lock_days) * 86400)}
                            save_json_file(ASAMI_DB, asami_list); st.success("🚓 সফলভাবে লকআপে চালান হয়েছে!"); time.sleep(0.5); st.rerun()
            with c_col2:
                st.markdown("#### 🕊️ আসামি খালাস করুন:")
                if asami_list:
                    free_suspect = st.selectbox("কাকে মুক্তি দিবেন?", options=list(asami_list.keys()))
                    if st.button("🔓 জেল থেকে মুক্তি দিন", use_container_width=True):
                        if free_suspect in asami_list: del asami_list[free_suspect]; save_json_file(ASAMI_DB, asami_list); st.success("মুক্ত ও আনলক করা হয়েছে!"); time.sleep(0.5); st.rerun()
        else: st.error("🔒 এই সেকশনটি শুধুমাত্র মেইন সিইও পোর্টাল দিয়ে এক্সেস করা যাবে।")

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v47.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
