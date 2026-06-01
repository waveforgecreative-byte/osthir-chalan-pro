import streamlit as st
import os
import json
import requests
import pandas as pd
import re
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- PREMIUM PAGE CONFIG ---
st.set_page_config(page_title="অস্থির চালান PRO", page_icon="⚡", layout="wide")

# --- CLOUD SAFE DATABASE MECHANISM (DATA RETENTION LOCKED) ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
HISTORY_DB = "users_history_memory.json"

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f: return json.load(f)
        except: return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

if "users_cache" not in st.session_state:
    st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state:
    st.session_state.config_cache = load_json_file(CONFIG_FILE, {
        "master_pin": "69", 
        "admin_pass": "reyadh123",
        "abstract_keys": [],
        "tomba_keys": [],
        "hunter_keys": []
    })
if "history_cache" not in st.session_state:
    st.session_state.history_cache = load_json_file(HISTORY_DB, {})

users = st.session_state.users_cache
config = st.session_state.config_cache
history = st.session_state.history_cache

# --- DESIGN UPGRADE: NEXT-GEN NEON EMERALD (V17.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght=500;600;700&family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
    
    /* Global Reset & Futuristic Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #060913 !important; 
        color: #E2E8F0 !important;
    }
    
    /* Glassmorphism Dynamic Cards */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 10px;
    }
    
    /* Advanced Typography & Gradient Title */
    .main-title { 
        font-family: 'Hind Siliguri', sans-serif !important; 
        font-size: 54px !important; 
        font-weight: 800 !important; 
        background: linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .sub-title { 
        color: #94A3B8; 
        font-size: 15px; 
        margin-bottom: 35px;
        font-weight: 500;
    }
    
    /* Custom Inputs (Focus Rings Style) */
    div.stTextInput > div > div > input, div.stTextArea > div > div > textarea { 
        background-color: #0E1322 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #1E293B !important; 
        border-radius: 12px !important; 
        padding: 14px !important;
        font-size: 15px;
        transition: all 0.3s ease;
    }
    div.stTextInput > div > div > input:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }
    
    /* Cyber Emerald Premium Buttons */
    div.stButton > button { 
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important; 
        color: #060913 !important; 
        border-radius: 12px !important; 
        font-weight: 800; 
        font-size: 16px;
        padding: 14px 30px !important; 
        border: none !important; 
        width: 100%; 
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div.stButton > button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.45);
        color: #000000 !important;
    }
    
    /* Sleek Expander Override */
    .streamlit-expanderHeader {
        background-color: #0E1322 !important;
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
    }
    
    /* Footer Customization */
    .footer { 
        position: fixed; 
        left: 0; 
        bottom: 0; 
        width: 100%; 
        background-color: #060913; 
        color: #64748B; 
        text-align: center; 
        padding: 14px; 
        font-size: 13px; 
        border-top: 1px solid rgba(255, 255, 255, 0.05); 
        z-index: 999; 
    }
    .footer span { 
        color: #10B981; 
        font-weight: 700; 
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "last_scrap_time" not in st.session_state: st.session_state.last_scrap_time = 0

# --- SMART EMAIL VALIDATOR ---
def check_email_real_or_fake(email):
    abstract_keys = config.get("abstract_keys", [])
    for key in abstract_keys:
        try:
            url = f"https://emailvalidation.abstractapi.com/v1/?api_key={key.strip()}&email={email}"
            res = requests.get(url, timeout=3).json()
            if "deliverability" in res:
                return "Real ✅" if res["deliverability"] == "DELIVERABLE" else "Risky ⚠️"
        except: continue
    return "Not Checked (No API Key) 🔄"

# --- DEEP WEB EMAIL HUNTER WITH TOMBA & HUNTER.IO ---
def advanced_email_hunter(url):
    if not url or url == "N/A" or "google.com" in url: return "N/A"
    try:
        if not url.startswith("http"): url = "http://" + url
        res = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        emails = re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z0-9.\-_]+', res.text)
        invalid_keywords = ['user@domain.com', 'email@domain.com', 'yourname@', 'example@', 'sentry.io', '.png', '.jpg', '.jpeg', '.gif', 'wixpress.com', 'myemail@', 'test@test', 'domain.com', 'template']
        for e in emails:
            if not any(kw in e.lower() for kw in invalid_keywords):
                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', e): return e
    except: pass

    domain = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    tomba_keys = config.get("tomba_keys", [])
    for k in tomba_keys:
        try:
            t_url = f"https://api.tomba.io/v1/domain-search?domain={domain}"
            headers = {"X-Tomba-Key": k.strip(), "X-Tomba-Secret": "ts_"}
            t_res = requests.get(t_url, headers=headers, timeout=3).json()
            if "data" in t_res and t_res["data"].get("emails"):
                return t_res["data"]["emails"][0]["email"]
        except: continue

    hunter_keys = config.get("hunter_keys", [])
    for hk in hunter_keys:
        try:
            h_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={hk.strip()}"
            h_res = requests.get(h_url, timeout=3).json()
            if "data" in h_res and h_res["data"].get("emails"):
                return h_res["data"]["emails"][0]["value"]
        except: continue

    return "N/A"

# --- AUTHENTICATION INTERFACE ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">⚡ অস্থির চালান PRO</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Next-Gen Premium B2B Lead Engine</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color:#10B981;'>📝 Register ID</h3>", unsafe_allow_html=True)
        new_username = st.text_input("Choose Unique User ID:", key="reg_user")
        if st.button("Create Account"):
            if new_username.strip() == "": st.error("User ID ফাঁকা রাখা যাবে না!")
            elif new_username in users: st.warning("এই নামে আইডি আছে!")
            else:
                users[new_username] = {"status": "pending"}
                st.session_state.users_cache = users
                save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট তৈরি হয়েছে!")
    with col2:
        st.markdown("<h3 style='color:#10B981;'>🔓 System Login</h3>", unsafe_allow_html=True)
        login_username = st.text_input("User ID:", key="login_user")
        input_pin = st.text_input("Access Pin:", type="password", key="login_pin")
        if st.button("Unlock Dashboard 🚀"):
            if login_username not in users: st.error("❌ আইডি পাওয়া যায়নি!")
            elif input_pin != config["master_pin"]: st.error("❌ ভুল এক্সেস পিন!")
            else: st.session_state.logged_in_user = login_username; st.rerun()

# --- MAIN APP INTERFACE ---
else:
    current_user_id = st.session_state.logged_in_user
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown('<p class="main-title">⚡ অস্থির চালান PRO</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#10B981; font-weight:600; letter-spacing:0.5px;">🟢 SECURE NODE: {current_user_id.upper()} // LOAD-BALANCED ARCHITECTURE</p>', unsafe_allow_html=True)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Exit Portal 🚪"): st.session_state.logged_in_user = None; st.session_state.current_leads = []; st.rerun()

    # --- HYBRID REVOLUTION MULTI-LOADER ---
    def start_load_balanced_hunting(search_query, status_box, table_placeholder, user_id):
        if user_id not in history: history[user_id] = []
        user_scraped_memory = set(history[user_id])
        
        status_box.info("📡 ম্যাপস ক্রলার ও ফ্রি ব্যাকআপ ক্লাউড ইঞ্জিন সিঙ্ক করা হচ্ছে...")
        search_encoded = urllib.parse.quote(search_query)
        map_url = f"https://www.google.com/maps/search/{search_encoded}?hl=en"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"}
        
        leads = []
        try:
            res = requests.get(map_url, headers=headers, timeout=15)
            html_content = res.text
            
            potential_biz_names = re.findall(r'\[null,null,"([^"]+)",\[', html_content)
            potential_phones = re.findall(r'"([0-9\s\-\+\(\)]{7,20})"', html_content)
            potential_websites = re.findall(r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-z]{2,6}', html_content)
            
            clean_websites = list(set([w for w in potential_websites if "google.com" not in w and "gstatic.com" not in w and "schema.org" not in w][:100]))
            clean_names = list(set([b for b in potential_biz_names if len(b) > 3]))[:100]
            clean_phones = list(set([p.strip() for p in potential_phones if len(p.strip()) > 9]))[:100]
            
            if not clean_websites:
                ddg_url = "https://html.duckduckgo.com/html/"
                ddg_res = requests.post(ddg_url, data={'q': search_query}, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                links = re.findall(r'class="result__url"[^>]*href="([^"]*)"', ddg_res.text)
                for l in links:
                    if "uddg=" in l:
                        act_url = urllib.parse.unquote(l.split("uddg=")[1].split("&")[0])
                        if not any(x in act_url for x in ["facebook.com", "instagram.com", "linkedin.com"]):
                            clean_websites.append(act_url)
                clean_websites = list(set(clean_websites))[:100]

            status_box.info(f"⚡ ১০০ লিমিটের ভেতর {len(clean_websites)} টি ডেটা প্রসেস হচ্ছে। এপিআই রোটেশন সচল...")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                scraped_emails = list(executor.map(advanced_email_hunter, clean_websites))
                
            for idx, web_url in enumerate(clean_websites):
                if web_url in user_scraped_memory: continue
                
                biz_name = clean_names[idx] if idx < len(clean_names) else f"Premium Studio {idx+1}"
                phone_num = clean_phones[idx] if idx < len(clean_phones) else "N/A"
                email = scraped_emails[idx]
                
                email_status = "N/A"
                if email != "N/A":
                    email_status = check_email_real_or_fake(email)
                
                leads.append({
                    "Client Name": biz_name,
                    "Website": web_url,
                    "Email": email,
                    "Verification": email_status,
                    "Number": phone_num
                })
                history[user_id].append(web_url)
                table_placeholder.dataframe(pd.DataFrame(leads), use_container_width=True)
                
            st.session_state.history_cache = history
            save_json_file(HISTORY_DB, history)
            
        except Exception as e: status_box.error(f"Engine Warning: {str(e)}")
        return leads

    # --- UI SEARCH PANEL ---
    st.markdown("<h3 style='color:#10B981; font-family:\"Hind Siliguri\"'>🎯 হান্টার কনসোল (100 Auto-Limit Locked)</h3>", unsafe_allow_html=True)
    search_keyword = st.text_input("Enter Target Business & Location (e.g., Real Estate Agent in New York):")
    
    if st.button("LAUNCH HYBRID MEGA MOVEMENT ENGINE 🚀"):
        current_time = time.time()
        time_passed = current_time - st.session_state.last_scrap_time
        
        if time_passed < 120:
            st.error(f"🛑 গুগল ব্লক প্রোটেকশন লক! সেফটির জন্য আপনাকে আরও {int(120 - time_passed)} সেকেন্ড অপেক্ষা করতে হবে ভাই।")
        else:
            if search_keyword:
                status_box = st.empty(); table_placeholder = st.empty()
                results = start_load_balanced_hunting(search_keyword, status_box, table_placeholder, current_user_id)
                if results:
                    st.session_state.current_leads = results
                    st.session_state.last_scrap_time = time.time()
                    st.success(f"🔥 সফলভাবে ১০০ লিমিটের ভেতর {len(results)} টি রিয়েল ডাটা ম্যাপস ও ওয়েব থেকে আনা কমপ্লিট!")

    # --- RENDER DATABASE TABLE ---
    if st.session_state.current_leads:
        st.markdown("<h3 style='color:#10B981; font-family:\"Hind Siliguri\"'>📋 এক্সট্র্যাক্টেড লিড ডেটাবেস</h3>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)
        
        # --- SMART AI-STYLE CAMPAIGN ENGINE ---
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#10B981; font-family:\"Hind Siliguri\"'>⚡ সেলস কন্ট্রোল অ্যান্ড মেল ব্লাস্টার</h2>", unsafe_allow_html=True)
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            my_company = st.text_input("🏢 Your Company Name:", value="Reyadh Marketing Lab")
            my_role = st.text_input("👑 Your Role:", value="Founder")
        with col_inp2:
            my_services = st.text_input("🛠️ Services You Offer:", value="Premium Photo & Video Editing Services")
            target_reason = st.text_input("🎯 Reason to Approach:", value="spending too many sleepless nights editing wedding raw files")

        st.markdown("<h4 style='color:#10B981;'>📬 SMTP Server Configuration</h4>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1: custom_sender = st.text_input("Sender Gmail Account:", placeholder="brand@gmail.com")
        with col_m2: custom_app_pass = st.text_input("Google App Password:", type="password", placeholder="16-digit secret code")
            
        campaign_subject = st.text_input("Cold Mail Email Subject:", value="Loved your wedding portfolio! (Quick question)")
        
        def build_dynamic_cold_mail(client_name, company, role, services, reason):
            return f"Hello {client_name},\n\nI hope you are doing well. I stumbled upon your business profile and was highly impressed by your work!\n\nI am writing to you because I noticed that you might be {reason}. At {company}, we specialize in {services}.\n\nWould you be open to a short 5-minute call this week?\n\nBest regards,\n{role} | {company}"

        if st.button("LAUNCH AUTO-CAMPAIGN AND BLAST MAILS 🚀"):
            if not custom_sender.strip() or not custom_app_pass.strip(): st.error("❌ ইমেইল ও অ্যাপ পাসওয়ার্ড দিন!")
            else:
                success_count = 0
                try:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(custom_sender.strip(), custom_app_pass.strip())
                    for lead in st.session_state.current_leads:
                        to_email = lead["Email"]
                        if to_email != "N/A" and "@" in to_email and "domain.com" not in to_email.lower():
                            personal_msg = build_dynamic_cold_mail(lead["Client Name"], my_company, my_role, my_services, target_reason)
                            msg = MIMEMultipart()
                            msg["From"] = custom_sender; msg["To"] = to_email; msg["Subject"] = campaign_subject
                            msg.attach(MIMEText(personal_msg, "plain", "utf-8"))
                            server.sendmail(custom_sender, to_email, msg.as_string())
                            success_count += 1
                    server.quit()
                    st.success(f"🎯 সফলভাবে {success_count} জন ক্লায়েন্টকে মেইল অটো-ব্লাস্ট করা হয়েছে!")
                except Exception as e: st.error(f"Gmail System Error: {str(e)}")

# --- REYADH BHAI's MULTI-POOL CONTROL ROOM ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Reyadh Bhai's Secret Control Room (Premium API Center)"):
    admin_auth = st.text_input("Enter Secret Admin Password:", type="password", key="admin_auth_pass")
    if admin_auth == config["admin_pass"]:
        st.success("Access Granted, Owner Node Secure.")
        
        # ১. অ্যাবস্ট্রাক্ট এপিআই পুল ম্যানেজমেন্ট
        st.markdown("### 📧 1. Abstract Email Verification API Keys")
        ak_list = config.get("abstract_keys", [])
        st.write(ak_list)
        new_ak = st.text_input("Add Abstract API Key:")
        if st.button("Save Abstract Key"):
            if new_ak and new_ak not in ak_list: ak_list.append(new_ak); config["abstract_keys"] = ak_list; save_json_file(CONFIG_FILE, config); st.rerun()
            
        # ২. টোম্বা এপিআই পুল ম্যানেজমেন্ট
        st.markdown("### 🔍 2. Tomba.io Email Finder API Keys")
        tk_list = config.get("tomba_keys", [])
        st.write(tk_list)
        new_tk = st.text_input("Add Tomba API Key:")
        if st.button("Save Tomba Key"):
            if new_tk and new_tk not in tk_list: tk_list.append(new_tk); config["tomba_keys"] = tk_list; save_json_file(CONFIG_FILE, config); st.rerun()

        # ৩. হান্টার এপিআই পুল ম্যানেজমেন্ট
        st.markdown("### 🏹 3. Hunter.io API Keys")
        hk_list = config.get("hunter_keys", [])
        st.write(hk_list)
        new_hk = st.text_input("Add Hunter API Key:")
        if st.button("Save Hunter Key"):
            if new_hk and new_hk not in hk_list: hk_list.append(new_hk); config["hunter_keys"] = hk_list; save_json_file(CONFIG_FILE, config); st.rerun()

st.markdown('<div class="footer">Osthir Chalan Engine v17.0 | Handcrafted by <span>MD Reyadh</span></div>', unsafe_allow_html=True)
