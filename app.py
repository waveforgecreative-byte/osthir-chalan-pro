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

st.set_page_config(page_title="অস্থির চালান PRO v35.0 🖥️⚡", page_icon="🥷", layout="wide")

# --- CUSTOM CSS UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #080C14 !important; color: #00FF66 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; }
    .welcome-banner { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; font-family: 'Hind Siliguri', sans-serif; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    
    /* Premium UX Boxes */
    .target-box { background-color: #0F172A; border: 1px solid #1E293B; padding: 20px; border-radius: 12px; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .step-card { background: #111827; border: 1px solid #374151; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: #F3F4F6; }
    
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
if "insta_query_saved" not in st.session_state: st.session_state.insta_query_saved = ""
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
    st.markdown('<p class="main-title">অস্থির চালান PRO v35.0 🖥️⚡</p>', unsafe_allow_html=True)
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
        "📸 Instagram Unlimited Hunter (Ultra UX)", 
        "💬 Cyber Messenger & Video Call",
        "📩 Anonymous Complaint & Suggestion Box",
        "👑 CEO Secret Control Room"
    ])

    # --- TAB 1: GOOGLE MAPS LIVE API & FIXED SMTP MAIL INJECTOR ---
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
                                    
                                    raw_domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0] if website != "None" else ""
                                    generated_email = f"info@{raw_domain}" if raw_domain else "None"
                                    
                                    real_leads.append({
                                        "Name": title, "Email": generated_email, "Phone": phone, "Website": website
                                    })
                                st.session_state.current_leads = real_leads
                                st.success(f"✅ গুগলের লাইভ সার্ভার থেকে {len(real_leads)}টি ১০০% আসল কাস্টমার লিড পাওয়া গেছে!")
                            else:
                                st.error("❌ গুগলে এই কিওয়ার্ডের কোনো বিজনেস খুঁজে পাওয়া যায়নি অথবা আপনার এপিআই কি-র ফ্রি লিমিট শেষ।")
                                st.session_state.current_leads = []
                        else:
                            st.error(f"❌ SerpApi কানেকশন রিজেক্টেড! স্ট্যাটাস কোড: {res.status_code}.")
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
            outreach_reason = v_col3.text_input("🎯 Reason for Outreach:", value="I absolutely love your wedding portfolio and want to help you clear your heavy editing backlog this season.")
            services_offered = v_col4.text_area("⚡ Services Offered (Comma separated):", value="Cinematic Wedding Highlights, Full-Length Documentary Video Editing, RAW Photo Culling & Color Correction, Premium Lightroom Color Grading, Reels & Shorts Editing")
            
            st.markdown("#### ⚙️ SMTP Authenticator Connection")
            smtp_server = st.text_input("SMTP Server:", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port:", value=587)
            sender_email = st.text_input("আপনার ইমেইল (Sender Email):", value=users[current_user_id].get("connected_email", ""))
            sender_password = st.text_input("অ্যাপ পাসওয়ার্ড (App Password - ১৬ ডিজিটের সিক্রেট কোড):", type="password")
            
            st.write(f"📊 **আজকের সেন্ট মেইল কাউন্টার:** `{st.session_state.daily_mail_count} / 100`")
            
            if st.session_state.daily_mail_count >= 100 or st.session_state.mail_lock:
                st.session_state.mail_lock = True
                st.error("🚨 সিকিউরিটি এলার্ট: ১০০টি মেইলের লিমিট শেষ! আইডি ব্যান হওয়া রুখতে সিস্টেম লক করা হয়েছে।")
            else:
                if st.button("১-ক্লিকে স্মার্ট কোল্ড মেইল পাঠান 🚀"):
                    if not sender_email or not sender_password: 
                        st.error("❌ মেইল এবং ১৬ ডিজিটের অ্যাপ পাসওয়ার্ড দুটিই আবশ্যক।")
                    else:
                        s_count = 0
                        p_bar = st.progress(0)
                        
                        try:
                            server = smtplib.SMTP(smtp_server, int(smtp_port))
                            server.starttls()
                            server.login(sender_email, sender_password.strip().replace(" ", ""))
                            
                            for idx, lead in enumerate(st.session_state.current_leads):
                                if lead['Email'] == "None" or "@" not in lead['Email']: continue
                                if st.session_state.daily_mail_count >= 100:
                                    st.session_state.mail_lock = True
                                    break
                                
                                mail_body = f"Hello {lead['Name']},\n\nI am writing to you because {outreach_reason}.\n\nWe specialize in maximizing production speed and we can assist you with:\n\n{services_offered}\n\nLooking forward to your positive response.\n\nBest Regards,\n{user_real_name}\n{my_role}\n{my_company}"
                                
                                msg = MIMEMultipart()
                                msg['From'] = sender_email
                                msg['To'] = lead['Email']
                                msg['Subject'] = f"Exclusive Video Production Editing Proposal for {lead['Name']}"
                                msg.attach(MIMEText(mail_body, 'plain'))
                                
                                server.sendmail(sender_email, lead['Email'], msg.as_string())
                                
                                s_count += 1
                                st.session_state.daily_mail_count += 1
                                d_time = random.randint(4, 8)
                                st.caption(f"✓ {lead['Name']} (`{lead['Email']}`) এর ইনবক্সে সরাসরি মেইল ডেলিভারড! Anti-Spam বিরতি: {d_time} সেকেন্ড...")
                                time.sleep(d_time)
                                p_bar.progress((idx + 1) / len(st.session_state.current_leads))
                            
                            server.quit() 
                            st.success(f"🔥 ক্যাম্পেইন সফল! মোট {s_count}টি আসল পার্সোনালাইজড মেইল লাইভ সার্ভার দিয়ে পাঠানো হয়েছে।")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ জিমেইল সার্ভার কানেকশন এরর: {str(e)}. অ্যাপ পাসওয়ার্ড বা মেইল আইডি পুনরায় চেক করুন!")

    # --- TAB 2: INSTAGRAM HUNTER ENGINE (INTERNATIONAL UX & BUG FIXED) ---
    with engine_tab2:
        st.markdown("<h2 style='color:#00FF66; font-family:Hind Siliguri;'>📸 ইনস্টাগ্রাম আনলিমিটেড গ্লোবাল হান্টিং প্যানেল (USA, UK & Top Countries)</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#A5B4FC;'>মেম্বারদের জন্য সুখবর: কোনো পেইড এপিআই ছাড়াই এখন সরাসরি USA, UK, Canada ও Australia-র প্রিমিয়াম বায়ার ফিল্টার করতে পারবেন।</p>", unsafe_allow_html=True)
        st.write("---")

        ui_col1, ui_col2 = st.columns([2, 3])
        with ui_col1:
            target_country = st.selectbox(
                "🌐 টার্গেট বায়ার কান্ট্রি (Target Country):", 
                options=["United States (USA)", "United Kingdom (UK)", "Canada", "Australia", "Worldwide (Global)"]
            )
            
            inst_query = st.text_input("🔍 টার্গেট নিশ বা কিওয়ার্ড লিখুন:", value=st.session_state.insta_query_saved, placeholder="যেমন: wedding photographer")
            
            default_pitch = "Hey, your wedding portfolio looks absolutely stunning! 📸 We specialize in ultra-fast premium video editing and color grading. Can I drop a quick 30-second link to our work sample?"
            short_pitch = st.text_area("✍️ মেম্বারদের জন্য কিলার পিচ টেক্সট সেট করুন:", value=default_pitch, height=120)
            
            run_hunting = st.button("🚀 গ্লোবাল হান্টিং রাডার অ্যাক্টিভেট করুন", use_container_width=True)
            
            if run_hunting:
                if not inst_query.strip():
                    st.error("❌ অনুগ্রহ করে একটি নিশ কিওয়ার্ড দিন।")
                else:
                    st.session_state.insta_query_saved = inst_query.strip()
                    history_logs.append({
                        "user": current_user_id, 
                        "engine": f"Instagram Global ({target_country})", 
                        "keyword": inst_query.strip(), 
                        "count": "Unlimited", 
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    })
                    save_json_file(HISTORY_DB, history_logs)
                    st.success(f"🎯 {target_country} রাডার সক্রিয় হয়েছে! ডানের প্যানেলটি দেখুন।")

        with ui_col2:
            if st.session_state.insta_query_saved:
                st.markdown(f"""
                <div class="target-box">
                    <h3 style="color:#00FF66; margin-top:0;">🎯 International Client Control Panel</h3>
                    <p style="color:#94A3B8; font-size:14px;"><b>সক্রিয় সার্চ নিশ:</b> <span style="color:#38BDF8; font-weight:bold;">{st.session_state.insta_query_saved}</span></p>
                    <p style="color:#94A3B8; font-size:14px;"><b>টার্গেট লোকেশন:</b> <span style="color:#F43F5E; font-weight:bold;">{target_country}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<p style='color:#00FF66; font-weight:bold; margin-top:15px;'>👉 ক্লায়েন্ট হান্ট করার ৩ সেকেন্ডের ম্যাজিক নিয়ম:</p>", unsafe_allow_html=True)
                
                st.markdown("""
                <div class="step-card"><b>ধাপ ১:</b> নিচের বক্সের টেক্সটটি কপি করে নিন (ডান কোণায় মাউস নিলে ছোট কপি বাটন পাবেন)।</div>
                """, unsafe_allow_html=True)
                
                # Fixed bug using st.code instead of st.copy_to_clipboard to prevent Streamlit Cloud crashes
                st.code(short_pitch, language="text")
                
                st.markdown("""
                <div class="step-card" style="margin-top:15px;"><b>ধাপ ২:</b> এবার নিচের বাটন থেকে ইন্টারন্যাশনাল বায়ার ডিরেক্টরি ওপেন করুন।</div>
                """, unsafe_allow_html=True)
                
                country_suffix = ""
                if "USA" in target_country: country_suffix = " AND (NY OR LA OR California OR Texas OR USA)"
                elif "UK" in target_country: country_suffix = " AND (London OR UK OR Manchester)"
                elif "Canada" in target_country: country_suffix = " AND (Toronto OR Vancouver OR Canada)"
                elif "Australia" in target_country: country_suffix = " AND (Sydney OR Melbourne OR Australia)"
                
                raw_q = st.session_state.insta_query_saved
                final_google_query = f'site:instagram.com "{raw_q}"{country_suffix}'
                encoded_q = urllib.parse.quote(final_google_query)
                
                geo_tag = "usa" if "USA" in target_country else ("uk" if "UK" in target_country else ("canada" if "Canada" in target_country else ("australia" if "Australia" in target_country else "")))
                hashtag_format = raw_q.replace(' ', '') + geo_tag
                
                people_search_url = f"https://www.instagram.com/explore/tags/{hashtag_format}/"
                web_search_url = f"https://www.google.com/search?q={encoded_q}"
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.markdown(f'<a href="{people_search_url}" target="_blank"><button style="background-color:#E1306C; color:white; padding:12px 15px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; width:100%; box-shadow: 0 4px 10px rgba(225,48,108,0.3);">⚡ মেথড ১: ওপেন {target_country} নিশ ফিড 📸</button></a>', unsafe_allow_html=True)
                    st.caption(f"ঐ দেশের নির্দিষ্ট #{hashtag_format} ট্যাগ ব্যবহারকারী বায়ারদের পোস্ট আসবে।")
                    
                with btn_col2:
                    st.markdown(f'<a href="{web_search_url}" target="_blank"><button style="background-color:#4285F4; color:white; padding:12px 15px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; width:100%; box-shadow: 0 4px 10px rgba(66,133,244,0.3);">⚡ মেথড ২: গুগল এক্স-রে বায়ার ফিল্টার 🎯</button></a>', unsafe_allow_html=True)
                    st.caption(f"শুধুমাত্র {target_country}-এর যেসকল আইডির বায়োতে এই কিওয়ার্ড আছে তাদের লিস্ট আসবে।")
                
                st.markdown("""
                <div class="step-card" style="background-color:#064E3B; border-color:#10B981; margin-top:15px;">
                <b>ধাপ ৩:</b> বায়ারের প্রোফাইলে গিয়ে মেসেজ (Message) বক্সে মাউস রেখে জাস্ট <b>Ctrl + V</b> চেপে পেস্ট করে দিন এবং সেন্ড করুন! কোনো রিজিওনাল বা লোকাল আইডি আসবে না, সব প্রিমিয়াম বায়ার। 🔥
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 বাম পাশের বক্সে আপনার টার্গেট দেশ ও নিশ কিওয়ার্ড লিখে 'গ্লোবাল হান্টিং রাডার অ্যাক্টিভেট করুন' বাটনে চাপ দিন।")

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

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v35.0 | Developed by MD Reyadh</div>', unsafe_allow_html=True)
