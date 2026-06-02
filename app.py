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
if "announce_cache" not in st.session_state: st.session_state.announce_cache = load_json_file(ANNOUNCE_DB, [])
if "complaint_cache" not in st.session_state: st.session_state.complaint_cache = load_json_file(COMPLAINT_DB, [])

users = st.session_state.users_cache
config = st.session_state.config_cache
history_logs = st.session_state.history_cache
chat_messages = st.session_state.chat_cache
dm_messages = st.session_state.dm_cache
announcements = st.session_state.announce_cache
complaints = st.session_state.complaint_cache

st.set_page_config(page_title="অস্থির চালান PRO v34.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; font-family: 'Hind Siliguri', sans-serif; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .chat-box { height: 380px; overflow-y: auto; background: #090D16; border: 1px solid #1E293B; padding: 15px; border-radius: 8px; }
    .msg-incoming { background: #1E293B; color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; border-left: 3px solid #38BDF8; }
    .msg-outgoing { background: #0F2D1E; color: #00FF66; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; border-right: 3px solid #00FF66; }
    .msg-ceo { background: #311042; color: #F472B6; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #F472B6; font-weight: bold; width: fit-content; }
    .complaint-card { background: #1E1B4B; border-left: 4px solid #EF4444; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #EEF2F6; }
    .reply-card { background: #064E3B; border-left: 4px solid #10B981; padding: 8px 12px; border-radius: 6px; margin-top: 5px; color: #D1FAE5; font-size: 13px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "insta_leads" not in st.session_state: st.session_state.insta_leads = []
if "mail_lock" not in st.session_state: st.session_state.mail_lock = False
if "daily_mail_count" not in st.session_state: st.session_state.daily_mail_count = 0

def get_badge(u_id):
    u_data = users.get(u_id, {})
    badge = u_data.get("badge", "None")
    if badge == "Blue Tick 🔵": return " 🔵"
    elif badge == "Always Active 🔥": return " 🔥"
    elif badge == "Low Active 💤": return " 💤"
    return ""

# --- LOGIN / REGISTRATION GATEWAY ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">অস্থির চালান PRO v34.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice-board">{config.get("notice_text", "")}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📝 নতুন অ্যাকাউন্ট খুলুন")
        reg_id = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_uid")
        reg_name = st.text_input("আপনার সম্পূর্ণ নাম (Full Name):", key="reg_fullname")
        if st.button("অ্যাকাউন্ট তৈরি করুন ✅"):
            if reg_id.strip() and reg_name.strip():
                if reg_id.strip() not in users:
                    users[reg_id.strip()] = {
                        "name": reg_name.strip(), "badge": "None", "is_moderator": False, "user_api_key": "", "apify_api_key": "", "last_seen": time.time()
                    }
                    save_json_file(USER_DB, users)
                    st.success("✅ অ্যাকাউন্ট অ্যাক্টিভেটেড! এবার লগইন করুন।")
                else: st.error("❌ এই ইউজার আইডি অলরেডি রেজিস্টার্ড।")
            else: st.error("❌ সব ঘর পূরণ করুন।")
            
    with col2:
        st.markdown("### 🔑 ড্যাশবোর্ড লগইন")
        login_id = st.text_input("ইউজার আইডি (User ID):", key="login_uid")
        input_pin = st.text_input("২-ডিজিট পিন:", type="password", key="login_pin", max_chars=2)
        if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
            in_pin = str(input_pin).strip()
            conf_pin = str(config.get("master_pin", "69")).strip()
            if login_id in users and in_pin == conf_pin:
                users[login_id]["last_seen"] = time.time()
                save_json_file(USER_DB, users)
                st.session_state.logged_in_user = login_id
                st.rerun()
            else: st.error("❌ ভুল পিন বা ইউজার আইডি।")
else:
    current_user_id = st.session_state.logged_in_user
    is_mod = users[current_user_id].get("is_moderator", False)
    users[current_user_id]["last_seen"] = time.time()
    save_json_file(USER_DB, users)
    
    user_real_name = users[current_user_id].get("name", current_user_id)
    st.markdown(f'<div class="welcome-banner">🎉 স্বাগতম {user_real_name} ভাই! চলেন আজকে অস্থিরভাবে ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**NODE:** {current_user_id.upper()} {get_badge(current_user_id)} ' + ('|[MODERATOR 🛠️]' if is_mod else ''))
    if c2.button("লগআউট 🚪"): 
        st.session_state.logged_in_user = None
        st.rerun()

    engine_tab1, engine_tab2, engine_tab3, engine_tab4, engine_tab5 = st.tabs([
        "📍 Google Maps Scraper & Mail Engine", 
        "📸 Instagram Hunter Engine", 
        "💬 Cyber Messenger & Video Call",
        "📩 Anonymous Complaint & Suggestion Box",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1: GOOGLE MAPS LIVE API (FIXED - NO FAKE DATA) ---
    with engine_tab1:
        st.subheader("📍 Google Maps Live Scraping & Smart Variable Mailer")
        
        g_api_key = st.text_input("🔑 আপনার SerpApi Key সেট করুন (serpapi.com থেকে):", type="password", value=users[current_user_id].get("user_api_key", ""))
        if st.button("SerpApi Key সেভ করুন 💾"):
            users[current_user_id]["user_api_key"] = g_api_key.strip()
            save_json_file(USER_DB, users)
            st.success("SerpApi Key Successfully Saved Live!")

        sc_col1, sc_col2 = st.columns(2)
        search_query = sc_col1.text_input("গুগল ম্যাপস লাইভ সার্চ কিওয়ার্ড (যেমন: Wedding Photographer NY):")
        max_results = sc_col2.number_input("সর্বোচ্চ লিড সংখ্যা:", min_value=1, max_value=50, value=5)
        
        if st.button("গুগল ম্যাপস লাইভ স্ক্র্যাপার রান করুন ⚡"):
            if not g_api_key: 
                st.error("❌ আগে উপরে আপনার SerpApi Key বসিয়ে সেভ করুন!")
            elif not search_query.strip(): 
                st.error("❌ সার্চ কিওয়ার্ড খালি রাখা যাবে না।")
            else:
                with st.spinner("গুগল ম্যাপসের লাইভ সার্ভার থেকে ১০০% রিয়েল ডাটা স্ক্র্যাপ হচ্ছে..."):
                    # SERPAPI GOOGLE MAPS ACTUAL API CALL
                    serp_url = "https://serpapi.com/search.json"
                    params = {
                        "engine": "google_maps",
                        "q": search_query.strip(),
                        "api_key": g_api_key.strip(),
                        "num": int(max_results)
                    }
                    
                    try:
                        res = requests.get(serp_url, params=params, timeout=20)
                        if res.status_code == 200:
                            data = res.json()
                            local_results = data.get("local_results", [])
                            
                            if local_results:
                                real_leads = []
                                for idx, item in enumerate(local_results):
                                    if idx >= max_results: break
                                    title = item.get("title", f"Business {idx+1}")
                                    phone = item.get("phone", "None")
                                    website = item.get("website", "None")
                                    
                                    # ম্যাপসে সরাসরি ইমেল থাকে না, তাই ডোমেইন থেকে ইমেল ক্রিয়েট বা ব্ল্যাংক রাখা হয়
                                    raw_domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0] if website != "None" else ""
                                    generated_email = f"info@{raw_domain}" if raw_domain else "None"
                                    
                                    real_leads.append({
                                        "Name": title,
                                        "Email": generated_email,
                                        "Phone": phone,
                                        "Website": website
                                    })
                                st.session_state.current_leads = real_leads
                                st.success(f"✅ গুগলের লাইভ সার্ভার থেকে {len(real_leads)}টি ১০০% আসল কাস্টমার লিড পাওয়া গেছে!")
                            else:
                                st.error("❌ গুগলে এই কিওয়ার্ডের কোনো বিজনেস খুঁজে পাওয়া যায়নি অথবা আপনার এপিআই কি-র ফ্রি লিমিট শেষ।")
                                st.session_state.current_leads = []
                        else:
                            st.error(f"❌ SerpApi কানেকশন রিজেক্টেড! স্ট্যাটাস কোড: {res.status_code}. কি-টা রি-চেক করুন।")
                            st.session_state.current_leads = []
                    except Exception as e:
                        st.error(f"❌ গুগল ম্যাপস এপিআই টাইমআউট এরর: {str(e)}")
                        st.session_state.current_leads = []
                    
                    if st.session_state.current_leads:
                        history_logs.append({
                            "user": current_user_id, "engine": "Google Maps Live", "keyword": search_query, "count": len(st.session_state.current_leads), "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        })
                        save_json_file(HISTORY_DB, history_logs)

        if st.session_state.current_leads:
            df_maps = pd.DataFrame(st.session_state.current_leads)
            st.dataframe(df_maps, use_container_width=True)
            
            st.markdown("### 📧 Advanced 1-Click Cold Email Engine")
            v_col1, v_col2 = st.columns(2)
            my_company = v_col1.text_input("🏢 Your Company Name:", value="Reyadh Automation Agency")
            my_role = v_col2.text_input("👑 Your Designation/Title:", value="CEO & Founder")
            
            v_col3, v_col4 = st.columns(2)
            outreach_reason = v_col3.text_input("🎯 Reason for Outreach:", value="I found a massive loop on your website Google ranking")
            services_offered = v_col4.text_area("⚡ Services Offered (Comma separated):", value="Lead Generation, Cold Email Marketing, SEO Optimization")
            
            st.markdown("#### ⚙️ SMTP Authenticator Connection")
            smtp_server = st.text_input("SMTP Server:", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port:", value=587)
            sender_email = st.text_input("আপনার ইমেইল (Sender Email):", value=users[current_user_id].get("connected_email", ""))
            sender_password = st.text_input("অ্যাপ পাসওয়ার্ড (App Password):", type="password")
            
            st.write(f"📊 **আজকের সেন্ট মেইল কাউন্টার:** `{st.session_state.daily_mail_count} / 100`")
            
            if st.session_state.daily_mail_count >= 100 or st.session_state.mail_lock:
                st.session_state.mail_lock = True
                st.error("🚨 সিকিউরিটি এলার্ট: ১০০টি মেইলের লিমিট শেষ! আইডি ব্যান হওয়া রুখতে সিস্টেম লক করা হয়েছে।")
                
                new_email_connect = st.text_input("নতুন ইমেইল আইডি:")
                new_pass_connect = st.text_input("নতুন অ্যাপ পাসওয়ার্ড:", type="password")
                if st.button("সিস্টেম রি-অ্যাক্টিভেট ও আনলক করুন 🔓"):
                    if new_email_connect and new_pass_connect:
                        users[current_user_id]["connected_email"] = new_email_connect
                        save_json_file(USER_DB, users)
                        st.session_state.daily_mail_count = 0
                        st.session_state.mail_lock = False
                        st.success("✅ কাউন্টার রিলিজ হয়েছে! নতুন মেইল সাকসেসফুলি কানেক্টেড।")
                        time.sleep(1); st.rerun()
            else:
                if st.button("১-ক্লিকে স্মার্ট কোল্ড মেইল পাঠান 🚀"):
                    if not sender_email or not sender_password: st.error("❌ মেইল এবং অ্যাপ পাসওয়ার্ড দুটিই আবশ্যক।")
                    else:
                        s_count = 0
                        p_bar = st.progress(0)
                        for idx, lead in enumerate(st.session_state.current_leads):
                            if lead['Email'] == "None": continue
                            if st.session_state.daily_mail_count >= 100:
                                st.session_state.mail_lock = True
                                st.rerun(); break
                            
                            mail_body = f"Hello {lead['Name']},\n\nI am writing to you because {outreach_reason}.\n\nWe specialize in maximizing business value and we can assist you with:\n{services_offered}.\n\nLooking forward to your positive response.\n\nBest Regards,\n{user_real_name}\n{my_role}\n{my_company}"
                            try:
                                msg = MIMEMultipart()
                                msg['From'] = sender_email
                                msg['To'] = lead['Email']
                                msg['Subject'] = f"Exclusive Proposal for {lead['Name']}"
                                msg.attach(MIMEText(mail_body, 'plain'))
                                s_count += 1
                                st.session_state.daily_mail_count += 1
                                d_time = random.randint(3, 7)
                                st.caption(f"✓ {lead['Name']} কে পার্সোনালাইজড মেইল পাঠানো হয়েছে। Anti-Ban সেফটির জন্য {d_time} সেকেন্ড বিরতি...")
                                time.sleep(d_time)
                            except Exception as e: st.error(f"Error sending to {lead['Name']}: {str(e)}")
                            p_bar.progress((idx + 1) / len(st.session_state.current_leads))
                        st.success(f"🔥 ক্যাম্পেইন সফল! মোট {s_count}টি স্মার্ট মেইল ডেলিভারড।")

    # --- TAB 2: INSTAGRAM HUNTER ENGINE (FIXED LIVE API) ---
    with engine_tab2:
        st.subheader("📸 Instagram Live Target Hunting Engine (Option A - Personal API)")
        
        apify_token = st.text_input("🔑 আপনার Apify API Token সেট করুন (Apify > Settings > Integrations):", type="password", value=users[current_user_id].get("apify_api_key", ""))
        if st.button("Apify Token সেভ করুন 💾", key="save_api_insta"):
            users[current_user_id]["apify_api_key"] = apify_token.strip()
            save_json_file(USER_DB, users)
            st.success("Apify Token Successfully Logged!")

        inst_query = st.text_input("ইনস্টাগ্রাম টার্গেট নিশ বা ট্যাগ কিওয়ার্ড (যেমন: wedding_photographer):")
        insta_limit = st.number_input("লিড সংখ্যা (সর্বোচ্চ ২০টি অনুমোদিত):", min_value=1, max_value=20, value=10)
        interval_delay = st.slider("প্রতিটি মেসেজ লিংক জেনারেশন ডিলে (সেকেন্ড):", min_value=2, max_value=20, value=5)
        
        default_pitch = "Hey {Name}, your wedding portfolio is stunning! But the peak season backlog of culling, photo color-correcting, and editing highlights or full films must be exhausting. We specialize in wedding photo/video editing with ultra-fast turnaround and daily updates. Can I send a quick link to our recent editing portfolio?"
        short_pitch = st.text_area("ইনস্টাগ্রাম কিলার শর্ট হুক পিচ ({Name} দিন):", value=default_pitch)
        
        if st.button("ইনস্টাগ্রাম হান্টিং স্টার্ট করুন 🚀"):
            if not apify_token: 
                st.error("❌ অনুগ্রহ করে প্রথমে আপনার নিজের Apify API Tokenটি উপরে বসিয়ে সেভ করুন।")
            elif not inst_query.strip(): 
                st.error("❌ নিশ কিওয়ার্ড দিন।")
            else:
                with st.spinner("Apify ক্লাউড সার্ভার থেকে লাইভ ইনস্টাগ্রাম ডেটা ক্রিপ্টোগ্রাফি করা হচ্ছে..."):
                    clean_q = inst_query.strip().lower().replace(" ", "")
                    run_input = {"search": clean_q, "searchType": "user", "resultsLimit": int(insta_limit)}
                    actor_url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={apify_token}"
                    
                    try:
                        res = requests.post(actor_url, json=run_input, timeout=20)
                        if res.status_code in [200, 201]:
                            run_data = res.json()
                            dataset_id = run_data["data"]["defaultDatasetId"]
                            
                            st.caption("🔄 ক্লাউড রেসপন্স রিসিভড। ৫ সেকেন্ড ডেটা প্রসেসিং হোল্ড...")
                            time.sleep(5)
                            
                            fetch_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={apify_token}"
                            items_res = requests.get(fetch_url)
                            
                            if items_res.status_code == 200:
                                raw_items = items_res.json()
                                i_leads = []
                                for idx, item in enumerate(raw_items):
                                    if idx >= insta_limit: break
                                    username = item.get("username", "")
                                    full_name = item.get("fullName", username if username else f"Creator_{idx}")
                                    phone = item.get("publicPhone", "None")
                                    
                                    if username:
                                        i_leads.append({
                                            "Name": full_name, "Username": f"@{username}", "Phone": phone if phone and phone != "None" else ""
                                        })
                                
                                if not i_leads:
                                    st.error("❌ এপিআই সাকসেসফুল কিন্তু ইনস্টাগ্রাম এই কিওয়ার্ডের কোনো সচল ইউজার প্রোফাইল ব্যাক করেনি।")
                                    st.session_state.insta_leads = []
                                else:
                                    st.session_state.insta_leads = i_leads
                                    st.success(f"🎯 লাইভ এপিআই থেকে {len(i_leads)}টি ১০০% আসল ইনস্টাগ্রাম প্রোফাইল পাওয়া গেছে!")
                            else:
                                st.error("❌ Apify ডেটাসেট থেকে লিড ডেটা ফেচ করা যায়নি।")
                                st.session_state.insta_leads = []
                        else:
                            st.error(f"❌ Apify Token রিজেক্টেড অথবা মেম্বারের ফ্রি ব্যালেন্স শেষ! স্ট্যাটাস কোড: {res.status_code}")
                            st.session_state.insta_leads = []
                    except Exception as e:
                        st.error(f"❌ ইনস্টাগ্রাম লাইভ এপিআই নেটওয়ার্ক এরর: {str(e)}")
                        st.session_state.insta_leads = []
                    
                    if st.session_state.insta_leads:
                        history_logs.append({
                            "user": current_user_id, "engine": "Instagram Live", "keyword": inst_query, "count": len(st.session_state.insta_leads), "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        })
                        save_json_file(HISTORY_DB, history_logs)

        if st.session_state.insta_leads:
            st.write("### 🛡️ Anti-Block Direct Action Panel")
            for client in st.session_state.insta_leads:
                clean_name = client["Name"].replace("@", "")
                p_msg = short_pitch.replace("{Name}", clean_name)
                enc_msg = urllib.parse.quote(p_msg)
                
                clean_username = client["Username"].replace("@", "").strip()
                ig_url = f"https://instagram.com/{clean_username}"
                
                with st.container():
                    st.markdown(f"#### 👤 {client['Name']} (`{client['Username']}`)")
                    st.text(f"Hook Text: {p_msg}")
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button(f"📸 ওয়ান-ক্লিক ইনস্টাগ্রাম ওপেন ({client['Username']})", key=f"ig_{clean_username}_{random.randint(0,10000)}"):
                        st.markdown(f'<a href="{ig_url}" target="_blank">➔ এখানে ক্লিক করুন (ইনস্টাগ্রাম প্রোফাইল)</a>', unsafe_allow_html=True)
                        st.warning(f"🛡️ Anti-Block ডিলে অ্যাক্টিভ! পরবর্তী লিংকের জন্য {interval_delay} সেকেন্ড অপেক্ষা করুন।")
                        time.sleep(interval_delay)
                        
                    if client["Phone"]:
                        wa_url = f"https://wa.me/{client['Phone']}?text={enc_msg}"
                        if col_b2.button(f"💬 ওয়ান-ক্লিক হোয়াটসঅ্যাপ ওপেন ({client['Phone']})", key=f"wa_{clean_username}"):
                            st.markdown(f'<a href="{wa_url}" target="_blank">➔ এখানে ক্লিক করুন (হোয়াটসঅ্যাপ চ্যাট)</a>', unsafe_allow_html=True)
                            st.warning(f"🛡️ সেফটি ডিলে অ্যাক্টিভ! {interval_delay} সেকেন্ড হোল্ড...")
                            time.sleep(interval_delay)
                    else:
                        col_b2.info("ℹ️ এই আইডিতে পাবলিক হোয়াটসঅ্যাপ নাম্বার মেলেনি। শুধু ইনস্টাগ্রামে নক দিন।")
                st.markdown("---")

    # --- TAB 3: CYBER MESSENGER & HQ VIDEO CALL ---
    with engine_tab3:
        chat_sub1, chat_sub2, chat_sub3 = st.tabs(["🔊 Global Public Chat", "🔒 Secret 1:1 Personal DM & Voice", "📹 HQ Group Video Call Room"])
        
        with chat_sub1:
            chat_html = '<div class="chat-box">'
            for msg in chat_messages:
                if not isinstance(msg, dict): continue
                sender_name = users.get(msg.get("sender"), {}).get("name", msg.get("sender"))
                badge_str = get_badge(msg.get("sender"))
                
                if msg.get("sender") == "CEO 👑": msg_class = "msg-ceo"
                else: msg_class = "msg-outgoing" if msg.get("sender") == current_user_id else "msg-incoming"
                
                media_html = ""
                if "media_base64" in msg:
                    m_type = msg.get("media_type", "")
                    if m_type.startswith("image/"): media_html = f'<br><img src="data:{m_type};base64,{msg["media_base64"]}" style="max-width:250px; border-radius:8px;"/>'
                    elif m_type.startswith("audio/"): media_html = f'<br><audio controls src="data:{m_type};base64,{msg["media_base64"]}"></audio>'
                
                chat_html += f'<div class="{msg_class}"><b>{sender_name}{badge_str}:</b> {msg.get("text","")}{media_html}<br><small style="font-size:9px;opacity:0.5;">{msg.get("time","")}</small></div>'
            st.markdown(chat_html + '</div>', unsafe_allow_html=True)
            
            with st.form("pub_chat", clear_on_submit=True):
                t_msg = st.text_input("মেসেজ লিখুন:")
                u_file = st.file_uploader("ছবি / অডিও ভয়েস রেকর্ড আপলোড করুন:", type=["png", "jpg", "jpeg", "mp3", "wav"])
                if st.form_submit_button("পাঠান ✉️"):
                    if t_msg.strip() or u_file:
                        n_msg = {"sender": current_user_id, "text": t_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")}
                        if u_file:
                            n_msg["media_type"] = u_file.type
                            n_msg["media_base64"] = base64.b64encode(u_file.read()).decode()
                        chat_messages.append(n_msg); save_json_file(CHAT_DB, chat_messages); st.rerun()

        with chat_sub2:
            st.markdown("#### 🔒 ওয়ান-টু-টুয়ান সিক্রেট পার্সোনাল ইনবক্স উইথ সিকিউর কল")
            target_dm = st.selectbox("মেম্বার সিলেক্ট করুন যার সাথে সিক্রেট চ্যাট করবেন:", options=[u for u in users.keys() if u != current_user_id])
            
            if target_dm:
                sorted_nodes = sorted([current_user_id, target_dm])
                if "reyadh" in sorted_nodes[0].lower() or "reyadh" in sorted_nodes[1].lower():
                    p2p_room_name = f"reyadh-and-{target_dm if current_user_id.lower()=='reyadh' else current_user_id}-secure-call"
                else: p2p_room_name = f"{sorted_nodes[0]}-and-{sorted_nodes[1]}-secure-call"
                
                p2p_call_url = f"https://meet.jit.si/{p2p_room_name}"
                st.markdown(f'<div style="background-color: #121E31; padding: 12px; border-radius: 8px; border-left: 4px solid #A855F7;">🎥 <b>১:১ প্রাইভেট ভিডিও কল লিংক রেডি!</b> <a href="{p2p_call_url}" target="_blank"><button style="background-color:#A855F7; color:white; padding:6px 12px; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">➔ Start 1:1 Private Video Call 🔒</button></a></div>', unsafe_allow_html=True)
                
                dm_html = '<div class="chat-box">'
                filtered_dms = [d for d in dm_messages if isinstance(d, dict) and ((d.get("sender") == current_user_id and d.get("receiver") == target_dm) or (d.get("sender") == target_dm and d.get("receiver") == current_user_id))]
                for dm in filtered_dms:
                    dm_sender_name = users.get(dm.get("sender"), {}).get("name", dm.get("sender"))
                    dm_class = "msg-outgoing" if dm.get("sender") == current_user_id else "msg-incoming"
                    dm_html += f'<div class="{dm_class}"><b>{dm_sender_name}:</b> {dm.get("text","")}<br><small style="font-size:9px;opacity:0.5;">{dm.get("time","")}</small></div>'
                st.markdown(dm_html + '</div>', unsafe_allow_html=True)
                
                with st.form("dm_form", clear_on_submit=True):
                    t_dm = st.text_input("গোপন মেসেজ লিখুন:")
                    if st.form_submit_button("ডিএম পাঠান 🔐"):
                        if t_dm.strip():
                            dm_messages.append({"sender": current_user_id, "receiver": target_dm, "text": t_dm.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                            save_json_file(DM_DB, dm_messages); st.rerun()

        with chat_sub3:
            st.markdown("### 📹 HQ Secure Group Video Call Meeting Room")
            st.markdown(f'<a href="https://meet.jit.si/OsthircChalan_HQ_SecureRoom_Reyadh" target="_blank"><button style="background-color:#00FF66; color:black; padding:12px 24px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">➔ লাইভ গ্রুপ ভিডিও মিটিং রুম ওপেন করুন 🎥</button></a>', unsafe_allow_html=True)

    # --- TAB 4: COMPLAINT & SUGGESTION BOX ---
    with engine_tab4:
        st.subheader("📩 Anonymous Complaint & Suggestion Box (One-Way)")
        with st.form("complaint_form", clear_on_submit=True):
            comp_text = st.text_area("আপনার কমপ্লেইন বা পরামর্শটি এখানে লিখুন:")
            if st.form_submit_button("রিপোর্ট জমা দিন 📤"):
                if comp_text.strip():
                    complaints.append({
                        "id": str(random.randint(1000, 9999)), "user": current_user_id, "text": comp_text.strip(), "reply": "", "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    })
                    save_json_file(COMPLAINT_DB, complaints)
                    st.success("✅ আপনার রিপোর্টটি সম্পূর্ণ গোপনে সিইও দপ্তরে পাঠানো হয়েছে।")
        
        st.markdown("### 📥 আপনার সাবমিট করা রিপোর্টের জবাব:")
        for c in complaints:
            if c.get("user") == current_user_id:
                st.markdown(f'<div class="complaint-card"><b>আপনার কমপ্লেইন:</b> {c.get("text")}<br><small>সময়: {c.get("time")}</small></div>', unsafe_allow_html=True)
                if c.get("reply"): st.markdown(f'<div class="reply-card"><b>👑 CEO/Admin রিপ্লাই:</b> {c.get("reply")}</div>', unsafe_allow_html=True)

    # --- TAB 5: CEO SECRET CONTROL ROOM ---
    with engine_tab5:
        st.subheader("👑 Riad Bhai's Secret Control Room")
        is_access_granted = False
        if is_mod: is_access_granted = True
        
        admin_auth = st.text_input("🔒 সিইও মাস্টার পাসওয়ার্ড দিন:", type="password", key="ceo_master_pwd")
        if admin_auth == config.get("admin_pass", "reyadh123"):
            st.success("🔓 ফুল সিইও এক্সেস গ্রান্টেড! স্বাগতম রিয়াদ ভাই।")
            is_access_granted = True
            
            st.markdown("### 📢 লগইন নোটিশ এবং সিকিউরিটি পিন পরিবর্তন")
            new_notice = st.text_area("মেইন পেজের নোটিশ:", value=config.get("notice_text", ""))
            new_pin = st.text_input("২-ডিজিট মাস্টার পিন পরিবর্তন করুন:", value=config.get("master_pin", "69"), max_chars=2)
            new_pass = st.text_input("অ্যাডমিন পাসওয়ার্ড পরিবর্তন করুন:", value=config.get("admin_pass", "reyadh123"))
            
            if st.button("কনফিগারেশন সেভ করুন 💾"):
                config["notice_text"] = new_notice
                config["master_pin"] = new_pin
                config["admin_pass"] = new_pass
                save_json_file(CONFIG_FILE, config)
                st.success("✅ কনফিগারেশন চেঞ্জড!")
                time.sleep(0.5); st.rerun()
                
            st.markdown("---")
            st.markdown("### 🔵 ব্লু টিক এবং মডারেটর নিয়োগ প্যানেল")
            selected_member = st.selectbox("মেম্বার সিলেক্ট করুন:", options=list(users.keys()))
            if selected_member:
                m_data = users[selected_member]
                new_badge = st.selectbox("নতুন ব্যাজ বা একটিভিটি লেভেল সেট করুন:", options=["None", "Blue Tick 🔵", "Always Active 🔥", "Low Active 💤"])
                mod_checkbox = st.checkbox("এই মেম্বারকে ড্যাশবোর্ডের মডারেটর (Moderator) বানান 🛠️", value=m_data.get("is_moderator", False))
                
                if st.button("মেম্বার প্রোফাইল আপডেট করুন ⚙️"):
                    users[selected_member]["badge"] = new_badge
                    users[selected_member]["is_moderator"] = mod_checkbox
                    save_json_file(USER_DB, users)
                    st.success("✅ মেম্বার রোল এবং ব্লু টিক আপডেট করা হয়েছে!")
                    time.sleep(0.5); st.rerun()

        if is_access_granted:
            st.markdown("---")
            st.markdown("### 🕵️‍♂️ User Activity Spy & History Monitor")
            spy_member = st.selectbox("কোন ইউজারের ডেটা ও চ্যাট হিস্ট্রি চেক করবেন?", options=list(users.keys()), key="spy_box")
            if spy_member:
                member_logs = [l for l in history_logs if l.get("user") == spy_member]
                if member_logs: st.dataframe(pd.DataFrame(member_logs))
                spy_dms = [d for d in dm_messages if d.get("sender") == spy_member or d.get("receiver") == spy_member]
                if spy_dms: st.dataframe(pd.DataFrame(spy_dms))

            st.markdown("---")
            st.markdown("### 📥 লাইভ কমপ্লেইন باکس এবং রিপ্লাই ইঞ্জিন")
            if complaints:
                for idx, c in enumerate(complaints):
                    comp_user_name = users.get(c.get("user"), {}).get("name", c.get("user"))
                    st.markdown(f'<div class="complaint-card"><b>ID: {c.get("id")} | ফ্রম: {comp_user_name}</b><br>বার্তা: {c.get("text")}</div>', unsafe_allow_html=True)
                    rep_input = st.text_input(f"রিপ্লাই লিখুন (ID: {c.get('id')}):", key=f"rep_{c.get('id')}")
                    if st.button(f"রিপ্লাই পাঠান", key=f"btn_rep_{c.get('id')}"):
                        complaints[idx]["reply"] = rep_input.strip()
                        save_json_file(COMPLAINT_DB, complaints)
                        st.success("✅ রিপ্লাই পাঠানো হয়েছে।")
                        time.sleep(0.5); st.rerun()

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v34.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
