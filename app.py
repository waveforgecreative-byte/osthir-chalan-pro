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
st.set_page_config(page_title="অস্থির চালান PRO", page_icon="💼", layout="wide")

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
        "notice_text": "স্বাগতম অস্থির চালান PRO v20.0 তে! সার্ভার নোড সম্পূর্ণ সচল আছে। নিরবচ্ছিন্ন লিড হান্টিং উপভোগ করুন।",
        "abstract_keys": [],
        "tomba_keys": [],
        "hunter_keys": []
    })
if "history_cache" not in st.session_state:
    st.session_state.history_cache = load_json_file(HISTORY_DB, {})

users = st.session_state.users_cache
config = st.session_state.config_cache
history = st.session_state.history_cache

# --- DESIGN UPGRADE: MATTE MINIMALIST SLATE DEEP (V21.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Matte Minimalist Base Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Hind Siliguri', sans-serif !important;
        background-color: #0B0F19 !important; 
        color: #F1F5F9 !important;
    }
    
    /* Elegant SaaS Dataframe Box */
    div[data-testid="stDataFrame"] {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 8px;
        padding: 4px;
    }
    
    /* Labels & Standard Text Overrides */
    .stText, div[data-testid="stMarkdownContainer"] p, label {
        color: #CBD5E1 !important;
        font-weight: 500;
        font-family: 'Hind Siliguri', sans-serif !important;
    }
    
    /* Clean Premium Title Structure */
    .main-title { 
        font-family: 'Hind Siliguri', sans-serif !important; 
        font-size: 45px !important; 
        font-weight: 700 !important; 
        color: #F8FAFC !important;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    .sub-title { 
        color: #64748B; 
        font-size: 15px; 
        margin-bottom: 25px;
        font-weight: 400;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Notice Board - Exact Original Styling Saved */
    .notice-board {
        background-color: #111827;
        border-left: 4px solid #38BDF8;
        border-top: 1px solid #1F2937;
        border-right: 1px solid #1F2937;
        border-bottom: 1px solid #1F2937;
        padding: 15px;
        border-radius: 4px 8px 8px 4px;
        margin-bottom: 25px;
    }
    .notice-title {
        color: #38BDF8;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
        font-family: 'Inter', sans-serif !important;
    }
    .notice-content {
        color: #E2E8F0;
        font-size: 15px;
        font-family: 'Hind Siliguri', sans-serif !important;
    }
    
    /* Luxury Matte Form Controls */
    div.stTextInput > div > div > input, div.stTextArea > div > div > textarea { 
        background-color: #111827 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #1F2937 !important; 
        border-radius: 8px !important; 
        padding: 12px !important;
        font-size: 14px;
        transition: border-color 0.2s ease;
    }
    div.stTextInput > div > div > input:focus {
        border-color: #38BDF8 !important;
        box-shadow: none !important;
    }
    
    /* Non-Khet Minimal Premium Matte Blue Button */
    div.stButton > button { 
        background-color: #1E293B !important; 
        color: #38BDF8 !important; 
        border: 1px solid #334155 !important;
        border-radius: 8px !important; 
        font-weight: 600; 
        font-size: 14px;
        font-family: 'Hind Siliguri', sans-serif !important;
        padding: 12px 24px !important; 
        width: 100%; 
        transition: all 0.2s ease;
    }
    div.stButton > button:hover { 
        background-color: #38BDF8 !important;
        color: #0F172A !important;
        border-color: #38BDF8 !important;
    }
    
    /* Clean Sleek WhatsApp List Card */
    .wa-card {
        background: #111827;
        border: 1px solid #1F2937;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .wa-link {
        color: #38BDF8 !important;
        font-weight: 600;
        text-decoration: none;
        font-family: 'Hind Siliguri', sans-serif !important;
    }
    .wa-link:hover {
        text-decoration: underline;
    }
    
    /* Minimalist Footer */
    .footer { 
        position: fixed; 
        left: 0; 
        bottom: 0; 
        width: 100%; 
        background-color: #0B0F19; 
        color: #475569; 
        text-align: center; 
        padding: 12px; 
        font-size: 12px; 
        border-top: 1px solid #1F2937; 
        z-index: 999; 
    }
    .footer span { color: #64748B; font-weight: 600; }
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
    return "যাচাই করা হয়নি 🔄"

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
    st.markdown('<p class="main-title">অস্থির চালান PRO</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Minimalist B2B Intelligence Console</p>', unsafe_allow_html=True)
    
    # নোটিশ বোর্ড (লগইন স্ক্রিন)
    st.markdown(f"""
    <div class="notice-board">
        <div class="notice-title">📢 System Notice Board</div>
        <div class="notice-content">{config.get("notice_text", "স্বাগতম অস্থির চালান PRO v20.0 তে! সার্ভার নোড সম্পূর্ণ সচল আছে। নিরবচ্ছিন্ন লিড হান্টিং উপভোগ করুন।")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>নতুন অ্যাকাউন্ট রেজিস্টার করুন</h4>", unsafe_allow_html=True)
        new_username = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_user")
        if st.button("অ্যাকাউন্ট তৈরি করুন"):
            if new_username.strip() == "": st.error("ইউজার আইডি দেওয়া বাধ্যতামূলক!")
            elif new_username in users: st.warning("এই আইডিটি অলরেডি রেজিস্ট্রিকৃত!")
            else:
                users[new_username] = {"status": "pending"}
                st.session_state.users_cache = users
                save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!")
    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>পোর্টাল লগইন</h4>", unsafe_allow_html=True)
        login_username = st.text_input("ইউজার আইডি (User ID):", key="login_user")
        input_pin = st.text_input("সিস্টেম এক্সেস পিন (PIN):", type="password", key="login_pin")
        if st.button("ড্যাশবোর্ড আনলক করুন 🚀"):
            if login_username not in users: st.error("❌ ইউজার আইডি পাওয়া যায়নি!")
            elif input_pin != config["master_pin"]: st.error("❌ ভুল সিস্টেম পিন!")
            else: st.session_state.logged_in_user = login_username; st.rerun()

# --- MAIN APP INTERFACE ---
else:
    current_user_id = st.session_state.logged_in_user
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown('<p class="main-title">অস্থির চালান PRO</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#64748B; font-weight:500; font-size:14px; font-family:\'Inter\';">Authorized Node: <span style="color:#38BDF8;">{current_user_id.upper()}</span> // Secure Operational Shell</p>', unsafe_allow_html=True)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("সেশন শেষ করুন 🚪"): st.session_state.logged_in_user = None; st.session_state.current_leads = []; st.rerun()

    # নোটিশ বোর্ড (প্রধান ড্যাশবোর্ড)
    st.markdown(f"""
    <div class="notice-board">
        <div class="notice-title">📢 System Notice Board</div>
        <div class="notice-content">{config.get("notice_text", "স্বাগতম অস্থির চালান PRO v20.0 তে! সার্ভার নোড সম্পূর্ণ সচল আছে। নিরবচ্ছিন্ন লিড হান্টিং উপভোগ করুন।")}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- HYBRID HUNTING CORE ---
    def start_load_balanced_hunting(search_query, status_box, table_placeholder, user_id):
        if user_id not in history: history[user_id] = []
        user_scraped_memory = set(history[user_id])
        
        status_box.info("ম্যাপিং লেয়ার এবং সেকেন্ডারি ওয়েব ইনডেক্স থেকে ডাটা ফিড সিঙ্ক করা হচ্ছে...")
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

            status_box.info(f"ডাটা অ্যারে প্রসেস করা হচ্ছে (১০০ পুল লিমিটের ভেতর {len(clean_websites)} টি সাইট পাওয়া গেছে)...")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                scraped_emails = list(executor.map(advanced_email_hunter, clean_websites))
                
            for idx, web_url in enumerate(clean_websites):
                if web_url in user_scraped_memory: continue
                
                biz_name = clean_names[idx] if idx < len(clean_names) else f"Studio Enterprise {idx+1}"
                phone_num = clean_phones[idx] if idx < len(clean_phones) else "N/A"
                email = scraped_emails[idx]
                
                # ফিল্টারিং: ইমেইল এবং ফোন উভয়ই না থাকলে লিস্টে আসবে না
                if email == "N/A" and phone_num == "N/A":
                    continue
                
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
            
        except Exception as e: status_box.error(f"ইঞ্জিন ওয়ার্নিং: {str(e)}")
        return leads

    # --- UI SEARCH PANEL ---
    st.markdown("<h4 style='color:#F8FAFC; margin-top:20px;'>টার্গেট সার্চ প্যারামিটার</h4>", unsafe_allow_html=True)
    search_keyword = st.text_input("ব্যবসার ধরন এবং লোকেশন লিখুন (যেমন: Wedding Photographer in New York):")
    
    if st.button("ডাটা হার্ভেস্ট ইঞ্জিন চালু করুন 🚀"):
        current_time = time.time()
        time_passed = current_time - st.session_state.last_scrap_time
        
        if time_passed < 120:
            st.error(f"🛑 কুল-ডাউন প্রোটোকল সক্রিয়। গুগল ব্লক এড়াতে দয়া করে আরও {int(120 - time_passed)} সেকেন্ড অপেক্ষা করুন।")
        else:
            if search_keyword:
                status_box = st.empty(); table_placeholder = st.empty()
                results = start_load_balanced_hunting(search_keyword, status_box, table_placeholder, current_user_id)
                if results:
                    st.session_state.current_leads = results
                    st.session_state.last_scrap_time = time.time()
                    st.success(f"সফলভাবে {len(results)} টি ভ্যালিড ফিল্টার্ড প্রোফাইল প্রসেস করা হয়েছে।")

    # --- RENDER DATA MANAGEMENT GRID ---
    if st.session_state.current_leads:
        st.markdown("<h4 style='color:#F8FAFC; margin-top:30px;'>যাচাইকৃত লিড ডেটাবেস</h4>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.current_leads), use_container_width=True)
        
        # --- OUTBOUND CAMPAIGN CORE ---
        st.markdown("<hr style='border: 1px solid #1F2937;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#F8FAFC;'>আউটবাউন্ড ক্যাম্পেইন কন্ট্রোলার</h3>", unsafe_allow_html=True)
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            my_company = st.text_input("🏢 আপনার কোম্পানির নাম:", value="Reyadh Marketing Lab")
            my_role = st.text_input("👑 আপনার পদবি:", value="Founder")
        with col_inp2:
            my_services = st.text_input("🛠️ যে সার্ভিস অফার করছেন:", value="Premium Photo & Video Editing Services")
            target_reason = st.text_input("🎯 ক্লায়েন্টের মূল সমস্যা (Pain Point):", value="spending too many sleepless nights editing wedding raw files")

        st.markdown("<h5 style='color:#CBD5E1;'>আউটবাউন্ড ইমেইল নোড (SMTP কনফিগারেশন)</h5>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1: custom_sender = st.text_input("অথরাইজড জিমেইল অ্যাকাউন্ট:", placeholder="brand@gmail.com")
        with col_m2: custom_app_pass = st.text_input("জিমেইল অ্যাপ পাসওয়ার্ড (১৬-ডিジット):", type="password")
            
        campaign_subject = st.text_input("कোল্ড মেইল সাবজেক্ট লাইন:", value="Loved your wedding portfolio! (Quick question)")
        
        def build_dynamic_cold_mail(client_name, company, role, services, reason):
            return f"Hello {client_name},\n\nI hope you are doing well. I stumbled upon your business profile and was highly impressed by your work!\n\nI am writing to you because I noticed that you might be {reason}. At {company}, we specialize in {services}.\n\nWould you be open to a short 5-minute call this week?\n\nBest regards,\n{role} | {company}"

        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            st.markdown("<h5 style='color:#CBD5E1;'>ম্যাস কোল্ড মেইল ব্ল্যাস্টার</h5>", unsafe_allow_html=True)
            if st.button("অটো-ক্যাম্পেইন ও মেইল ব্লাস্ট শুরু করুন 🚀"):
                if not custom_sender.strip() or not custom_app_pass.strip(): st.error("SMTP কনফিগারেশনের তথ্য দেওয়া হয়নি।")
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
                        st.success(f"সফলভাবে {success_count} টি কোল্ড ইমেইল পাঠানো হয়েছে।")
                    except Exception as e: st.error(f"মেল রিলে ইন্টারফেস ত্রুটি: {str(e)}")
                    
        with col_act2:
            st.markdown("<h5 style='color:#CBD5E1;'>ডাইরেক্ট হোয়াটসঅ্যাপ পিচ চ্যানেল</h5>", unsafe_allow_html=True)
            has_wa_data = False
            for lead in st.session_state.current_leads:
                num = lead["Number"]
                if num != "N/A" and num.strip() != "":
                    has_wa_data = True
                    clean_num = re.sub(r'\D', '', num)
                    if len(clean_num) == 10: 
                        clean_num = "1" + clean_num
                    
                    wa_msg = build_dynamic_cold_mail(lead["Client Name"], my_company, my_role, my_services, target_reason)
                    encoded_msg = urllib.parse.quote(wa_msg)
                    
                    st.markdown(f"""
                    <div class="wa-card">
                        👤 <b>{lead['Client Name']}</b> (📱 {num})<br>
                        👉 <a class="wa-link" href="https://api.whatsapp.com/send?phone={clean_num}&text={encoded_msg}" target="_blank">⚡ হোয়াটসঅ্যাপ পিচ উইন্ডো ওপেন করুন</a>
                    </div>
                    """, unsafe_allow_html=True)
            if not has_wa_data:
                st.info("সক্রিয় ফোন নাম্বারসহ কোনো ডেটা পাওয়া যায়নি।")

# --- REYADH BHAI's SECRET CONTROL ROOM ROOM (EXACT RESTORATION) ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Reyadh Bhai's Secret Control Room (User Database & API Pool)"):
    admin_auth = st.text_input("Enter Secret Admin Password:", type="password", key="admin_auth_pass")
    if admin_auth == config["admin_pass"]:
        st.success("Access Granted. Secure Node Online.")
        
        # নোটিশ বোর্ড আপডেট প্যানেল
        st.markdown("### 📢 Update Notice Board")
        current_notice = config.get("notice_text", "")
        updated_notice = st.text_area("নতুন নোটিশ লিখুন:", value=updated_notice if updated_notice else current_notice)
        if st.button("নোটিশ বোর্ড আপডেট করুন"):
            config["notice_text"] = updated_notice
            save_json_file(CONFIG_FILE, config)
            st.success("নোটিশ বোর্ড সফলভাবে আপডেট হয়েছে!")
            st.rerun()
            
        st.markdown("---")
        # ইউজার ম্যানেজমেন্ট প্যানেল
        st.markdown("### 👥 Registered Users Management")
        current_users = list(users.keys())
        if not current_users:
            st.write("No users registered yet.")
        else:
            for u in current_users:
                col_u, col_b = st.columns([3, 1])
                col_u.markdown(f"<p style='color:#FFFFFF; font-size:16px;'>👤 User ID: <b>{u}</b> (Status: {users[u].get('status', 'Active')})</p>", unsafe_allow_html=True)
                if col_b.button("Delete User ❌", key=f"del_{u}"):
                    del users[u]; st.session_state.users_cache = users
                    save_json_file(USER_DB, users); st.success(f"User {u} deleted!"); st.rerun()
        
        st.markdown("---")
        # API Pool Configurations
        st.markdown("### 📧 1. Abstract Email Verification API Keys")
        ak_list = config.get("abstract_keys", [])
        st.write(ak_list)
        new_ak = st.text_input("Add Abstract API Key:")
        if st.button("Save Abstract Key"):
            if new_ak and new_ak not in ak_list: ak_list.append(new_ak); config["abstract_keys"] = ak_list; save_json_file(CONFIG_FILE, config); st.rerun()
            
        st.markdown("### 🔍 2. Tomba.io Email Finder API Keys")
        tk_list = config.get("tomba_keys", [])
        st.write(tk_list)
        new_tk = st.text_input("Add Tomba API Key:")
        if st.button("Save Tomba Key"):
            if new_tk and new_tk not in tk_list: tk_list.append(new_tk); config["tomba_keys"] = tk_list; save_json_file(CONFIG_FILE, config); st.rerun()

        st.markdown("### 🏹 3. Hunter.io API Keys")
        hk_list = config.get("hunter_keys", [])
        st.write(hk_list)
        new_hk = st.text_input("Add Hunter API Key:")
        if st.button("Save Hunter Key"):
            if new_hk and new_hk not in hk_list: hk_list.append(new_hk); config["hunter_keys"] = hk_list; save_json_file(CONFIG_FILE, config); st.rerun()

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v21.0 | Developed by <span>MD Reyadh</span></div>', unsafe_allow_html=True)
