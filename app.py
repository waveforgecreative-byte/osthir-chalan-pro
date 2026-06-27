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
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 38px !important; font-weight: 700 !important; color: #00FF66 !important; text-shadow: 0 0 10px #00FF66; margin-bottom: 5px; }
    .dev-tag { font-size: 16px !important; color: #38BDF8 !important; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px; display: block; text-shadow: 0 0 5px #38BDF8; }
    .welcome-banner { background: linear-gradient(90deg, #1E1B4B, #311042); border-left: 5px solid #F472B6; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .welcome-banner-user { background: linear-gradient(90deg, #0F172A, #1E293B); border-left: 5px solid #00FF66; padding: 18px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF; }
    .notice-board { background-color: #0F172A; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #F1F5F9; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #060911; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1E293B; color: #64748B; z-index: 999; }
    .funny-warning { background: linear-gradient(135deg, #450A0A, #1A0505); border: 2px dashed #FF3333; padding: 20px; border-radius: 10px; color: #FFAAAA; text-align: center; font-size: 16px; font-weight: bold; margin-top: 15px; line-height: 1.6; box-shadow: 0 0 15px rgba(255,51,51,0.3); }
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
    st.markdown('<p class="dev-tag">💻 Developed by MD Reyadh</p>', unsafe_allow_html=True)
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
                else:
                    st.markdown("""
                    <div class="funny-warning">
                        🛑 আইহাহাহা! পিন তো হয় নাই রে মামা! <br>
                        খাতায় ভুলভাল পিন টিপলে ড্যাশবোর্ড খুলবে না। এইটার সিকিউরিটি অনেক কড়া! <br>
                        সোজা গিয়া <b>MD Reyadh</b> ভাইরে একটা কড়া মেসেজ দিয়া পিনটা চেয়ে নেন, নাইলে আজীবন এইখানেই বইসা থাকা লাগবো! 💀😉
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("💬 রিয়াদ ভাইরে মেসেজ দিন (পিন এর জন্য)", "https://m.me/your_messenger_id_here")

else:
    current_user_id = st.session_state.logged_in_user
    is_ceo_active = st.session_state.is_ceo
    user_real_name = "MD Reyadh" if is_ceo_active else users[current_user_id].get("name", current_user_id)
    
    # Header Branding for inner panels
    st.markdown('<p class="main-title">অস্থির চালান PRO v65.0 🖥️⚡</p>', unsafe_allow_html=True)
    st.markdown('<p class="dev-tag">💻 Developed by MD Reyadh</p>', unsafe_allow_html=True)
    
    if is_ceo_active: st.markdown(f'<div class="welcome-banner">👑 স্বাগতম রিয়াদ ভাই! মেইন সিইও প্যানেল একটিভ।</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="welcome-banner-user">🎉 স্বাগতম {user_real_name} ভাই! চলেন ক্লায়েন্ট হান্ট করা যাক... 🚀⚡</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'**ACTIVE NODE:** {current_user_id.upper()}')
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.session_state.is_ceo = False; st.rerun()

    saved_api = config.get("ceo_saved_api", "") if is_ceo_active else users.get(current_user_id, {}).get("user_api_key", "")
    saved_company = config.get("ceo_company", "Reyadh Agency") if is_ceo_active else users.get(current_user_id, {}).get("company_name", "")
    saved_role = config.get("ceo_role", "Founder & CEO") if is_ceo_active else users.get(current_user_id, {}).get("user_role", "CEO")
    saved_services = config.get("ceo_services", "Video Editing, Thumbnail Design") if is_ceo_active else users.get(current_user_id, {}).get("services", "")
    saved_email = config.get("ceo_email", "") if is_ceo_active else users.get(current_user_id, {}).get("sender_email", "")
    saved_app_pass = config.get("ceo_app_pass", "") if is_ceo_active else users.get(current_user_id, {}).get("app_pass", "")

    all_tabs = ["📍 Google Maps Scraper", "🏢 Premium Real Estate Sniper", "📸 Instagram AI Global Hunter", "💬 Cyber Messenger", "🚨 CEO Control Room"]
    tab_selection = st.radio("🗂️ নেভিগেশন মেনু:", all_tabs, index=st.session_state.active_tab_index, horizontal=True)
    st.session_state.active_tab_index = all_tabs.index(tab_selection)
    st.markdown("---")

    with st.expander("⚙️ আপনার গ্লোবাল এপিআই ও মেল কনফিগারেশন মেমরি প্যানেল"):
        p_col1, p_col2, p_col3 = st.columns(3)
        u_api_key = p_col1.text_input("🔑 SerpApi Key:", type="password", value=saved_api)
        u_company = p_col2.text_input("🏢 কোম্পানির নাম:", value=saved_company)
        u_role = p_col3.text_input("👔 পদবি:", value=saved_role)
        p_col4, p_col5 = st.columns(2)
        u_services = p_col4.text_input("⚡ আপনার সার্ভিসসমূহ:", value=saved_services)
        u_email = p_col5.text_input("📧 সেন্ডার জিমেইল:", value=saved_email)
        u_app_pass = st.text_input("🔒 জিমেইল অ্যাপ পাসওয়ার্ড:", type="password", value=saved_app_pass)
        
        if st.button("💾 গ্লোবাল প্রোফাইল ডাটা সার্ভারে পার্মানেন্ট সেভ করুন"):
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
            st.success("✅ কনফিগারেশন সার্ভারে সেভ হয়েছে!"); st.rerun()

    # --- TAB 1: GOOGLE MAPS SCRAPER ---
    if tab_selection == "📍 Google Maps Scraper":
        st.subheader("📍 Google Maps Advanced Lead Sniper Engine")
        col_s1, col_s2 = st.columns(2)
        search_query = col_s1.text_input("🎯 টার্গেটেড নিশ ও লোকেশন লিখুন (যেমন: 'Gym in New York'):", key="gm_query")
        search_limit = col_s2.number_input("📊 লিড লিমিট:", min_value=5, max_value=100, value=10, step=5, key="gm_limit")
        
        if st.button("🚀 ম্যাপস ডাটা এক্সট্রাক্ট করা শুরু করুন", key="gm_btn"):
            if not u_api_key: st.error("❌ আগে গ্লোবাল কনফিগারেশন থেকে SerpApi কী সেভ করুন।")
            else:
                with st.status("🛸 Lead Sniper Live Terminal Booting...", expanded=True) as status:
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
                                
                                is_duplicate = any(h.get("কোম্পানির নাম") == comp_name for h in history_leads)
                                if is_duplicate: continue
                                
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
                                    "ঠিকানা": place.get("address", "N/A")
                                })
                                new_counter += 1
                                if len(scrapped_leads) >= search_limit: break
                                
                            if scrapped_leads:
                                st.session_state.current_leads = scrapped_leads
                                history_leads.extend(scrapped_leads)
                                save_json_file(LEADS_HISTORY_DB, history_leads)
                                status.update(label="✅ Extraction Completed!", state="complete")
                            else:
                                status.update(label="⚠️ No New Unique Leads Found.", state="error")
                        else:
                            status.update(label="❌ No Results Found.", state="error")
                    except Exception as e:
                        status.update(label=f"❌ Error Occurred: {e}", state="error")

        if st.session_state.current_leads:
            st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)
            email_sub = st.text_input("📝 মেইলের সাবজেক্ট:", value=f"Proposal for {{Name}} from {u_company}", key="gm_sub")
            email_body = st.text_area("📄 মেইল বডি:", value=f"Hello {{Name}},\n\nWe offer {u_services}.", key="gm_body")
            if st.button("⚡ ফায়ার করুন (Bulk Auto Mailer)", key="gm_fire_btn"):
                fire_bulk_emails(st.session_state.current_leads, u_email, u_app_pass, email_sub, email_body)

    # --- TAB 2: PREMIUM REAL ESTATE SNIPER ---
    elif tab_selection == "🏢 Premium Real Estate Sniper":
        st.subheader("🏢 Exclusive Real Estate Verified Lead Sniper")
        col_re1, col_re2 = st.columns(2)
        re_query = col_re1.text_input("🎯 রিয়েল এস্টেট নিশ/সিটি লিখুন:", key="re_query")
        re_limit = col_re2.number_input("📊 কতগুলো লিড চান?", min_value=5, max_value=50, value=5, step=5, key="re_limit")
        
        if st.button("⚡ রিয়েল-টাইম রিয়েল এস্টেট হান্টিং শুরু করুন", key="re_btn"):
            if not u_api_key: st.error("❌ আগে গ্লোবাল প্যানেলে আপনার SerpApi কী সেভ করুন।")
            else:
                with st.status("🧬 Booting Lead Sniper Advanced Real Estate...", expanded=True) as status:
                    api_url = f"https://serpapi.com/search.json?engine=google_maps&q={urllib.parse.quote(re_query)}&hl=en&auth_user=0&api_key={u_api_key}"
                    try:
                        res = requests.get(api_url).json()
                        local_results = res.get("local_results", [])
                        history_leads = load_json_file(LEADS_HISTORY_DB, [])
                        verified_re_leads = []
                        new_counter = 1
                        
                        if local_results:
                            for place in local_results:
                                comp_name = place.get("title", "N/A")
                                comp_website = place.get("website", "N/A")
                                comp_phone = place.get("phone", "N/A")
                                
                                if any(h.get("কোম্পানির নাম") == comp_name for h in history_leads): continue
                                if comp_website == "N/A" or not comp_website: continue
                                if not is_valid_phone(comp_phone): continue
                                    
                                clean_domain = comp_website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
                                real_mail = f"info@{clean_domain}"
                                
                                if not is_valid_email(real_mail): continue
                                    
                                verified_re_leads.append({
                                    "ID": new_counter,
                                    "কোম্পানির নাম": comp_name,
                                    "ভেরিফাইড ফোন": comp_phone,
                                    "ওয়েবসাইট": comp_website,
                                    "রিয়েল ইমেইল": real_mail,
                                    "ঠিকানা": place.get("address", "N/A")
                                })
                                new_counter += 1
                                if len(verified_re_leads) >= re_limit: break
                                
                            if verified_re_leads:
                                st.session_state.re_leads = verified_re_leads
                                history_leads.extend(verified_re_leads)
                                save_json_file(LEADS_HISTORY_DB, history_leads)
                                status.update(label="✅ Extraction Done! Clean Data Saved.", state="complete")
                            else:
                                status.update(label="⚠️ No Fresh Verified Leads Found.", state="error")
                        else:
                            status.update(label="❌ Response Empty.", state="error")
                    except Exception as e:
                        status.update(label=f"❌ Error: {e}", state="error")

        if st.session_state.re_leads:
            st.dataframe(pd.DataFrame(st.session_state.re_leads), use_container_width=True)
            re_sub = st.text_input("📝 মেইলের সাবজেক্ট (Subject):", value=f"Proposal for {{Name}} - {u_company}", key="re_sub_inp")
            re_body = st.text_area("📄 ইমেইল বডি কাস্টমাইজ করুন:", value=f"Hello {{Name}},\n\nWe love your properties.", key="re_body_inp")
            if st.button("⚡ ১-ক্লিকে মেইল করুন", key="re_fire_btn"):
                fire_bulk_emails(st.session_state.re_leads, u_email, u_app_pass, re_sub, re_body)

    # --- OTHER TABS ---
    elif tab_selection == "📸 Instagram AI Global Hunter":
        st.subheader("📸 Instagram AI Global Hunter")
        st.info("🤖 ইনস্টাগ্রাম হান্টার মডিউলটি ব্যাকগ্রাউন্ড সার্ভারের সাথে সেভ মোডে রয়েছে।")
        
    elif tab_selection == "💬 Cyber Messenger":
        st.subheader("💬 Cyber Messenger")
        st.info("🔒 মেসেঞ্জার মেমরি লোড হচ্ছে...")
        
    elif tab_selection == "🚨 CEO Control Room":
        st.subheader("👑 CEO Secret Control Room")
        if is_ceo_active:
            st.success("⚡ এডমিন কন্ট্রোল ওপেনড।")
            st.json(config)
        else:
            st.error("🛑 আপনি এডমিন নন!")

# --- GLOBAL FOOTER WITH BRANDING ---
st.markdown('<div class="footer">অস্থির চালান PRO v65.0 • Developed by MD Reyadh • Powered by Live Sync Engine 🖥️⚡</div>', unsafe_allow_html=True)
