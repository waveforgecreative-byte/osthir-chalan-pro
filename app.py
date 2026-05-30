import streamlit as st
import os
import json
import requests
import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse

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

# আগের সেভ করা ডাটা ও এপিআই কি অক্ষত রাখার জন্য ক্যাশ চেকিং লজিক
if "users_cache" not in st.session_state:
    st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state:
    st.session_state.config_cache = load_json_file(CONFIG_FILE, {"master_pin": "69", "admin_pass": "reyadh123", "serp_api_key": ""})
if "history_cache" not in st.session_state:
    st.session_state.history_cache = load_json_file(HISTORY_DB, {})

users = st.session_state.users_cache
config = st.session_state.config_cache
history = st.session_state.history_cache

# --- PREMIUM CYBERBLUE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght=500;700&family=Plus+Jakarta+Sans:wght=400;600;700;800&display=swap');
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0A0F1D; color: #F1F5F9;
    }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 50px !important; font-weight: 800 !important; background: linear-gradient(135deg, #38BDF8 0%, #1D4ED8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .sub-title { color: #64748B; font-size: 15px; margin-bottom: 30px; }
    .notice-box { background: rgba(56, 189, 248, 0.1); border: 1px solid #38BDF8; padding: 20px; border-radius: 12px; font-family: 'Hind Siliguri', sans-serif !important; font-size: 18px; color: #38BDF8; text-align: center; margin-bottom: 20px; line-height: 1.6; }
    div.stTextInput > div > div > input, div.stTextArea > div > div > textarea { background-color: #141B2D !important; color: #FFFFFF !important; border: 1px solid #1E293B !important; border-radius: 12px !important; padding: 12px !important; }
    div.stButton > button { background: linear-gradient(135deg, #0284C7 0%, #1E40AF 100%) !important; color: #FFFFFF !important; border-radius: 12px !important; font-weight: 700; padding: 14px 30px !important; border: none !important; width: 100%; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3); }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4); }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0A0F1D; color: #475569; text-align: center; padding: 12px; font-size: 13px; border-top: 1px solid #1E293B; z-index: 999; }
    .footer span { color: #38BDF8; font-weight: 700; }
    
    #MainMenu, footer, .stAppDeployDropdown, div[data-testid="stStatusWidget"], 
    div[data-testid="stDecoration"], .stActionButton, div[data-testid="stManageAppButton"], 
    iframe[title="Manage app"], .stViewerBadge, div[data-testid="stViewerBadge"] {
        visibility: hidden !important; display: none !important; opacity: 0 !important; pointer-events: none !important;
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "current_leads" not in st.session_state:
    st.session_state.current_leads = []

# --- SMART EMAIL SCRAPER ENGINE WITH ADVANCED FAKE FILTER ---
def extract_email_from_website(url):
    if not url or url == "N/A" or "google.com" in url: return "N/A"
    try:
        if not url.startswith("http"): url = "http://" + url
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        emails = re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z0-9.\-_]+', res.text)
        
        # ভুয়া, স্যাম্পল এবং ইমেজ ফাইল ফিল্টার করার জন্য কি-ওয়ার্ড লিস্ট
        invalid_keywords = [
            'user@domain.com', 'email@domain.com', 'yourname@', 'example@', 
            'sentry.io', '.png', '.jpg', '.jpeg', '.gif', 'wixpress.com', 
            'myemail@', 'test@test', 'domain.com'
        ]
        valid_emails = []
        
        for e in emails:
            # চেক করা হচ্ছে ইমেইলের ভেতর কোনো ভুয়া শব্দ আছে কিনা
            if not any(keyword in e.lower() for keyword in invalid_keywords):
                # একদম নিখুঁত ইমেইল ফরম্যাট ভ্যালিডেশন
                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', e):
                    valid_emails.append(e)
                
        return valid_emails[0] if valid_emails else "N/A"
    except:
        return "N/A"

# --- AUTHENTICATION INTERFACE ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">⚡ অস্থির চালান PRO</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Secure Portal Access Gate</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔑 Get Access Info")
        if st.button("📢 Click to View Notice Board"):
            st.markdown(f'<div class="notice-box">📢 নোটিশ বোর্ড:<br>এই ওয়েবসাইটের এক্সেস পাইতে হইলে রিয়াদ ভাইকে মেসেজ দিয়া ২ ডিজিটের পিন চান 😂</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📝 Create User ID")
        new_username = st.text_input("Choose Unique User ID / Your Name:", key="reg_user")
        if st.button("Create Account & Save"):
            if new_username.strip() == "": st.error("User ID ফাঁকা রাখা যাবে না!")
            elif new_username in users: st.warning("এই নামে অলরেডি আইডি আছে!")
            else:
                users[new_username] = {"status": "pending"}
                st.session_state.users_cache = users
                save_json_file(USER_DB, users)
                st.success("✅ আইডি ক্রিয়েট হয়েছে! এখন লগইন করুন।")
                
    with col2:
        st.markdown("### 🔓 Enter Secure Pin to Access")
        login_username = st.text_input("Enter Registered User ID:", key="login_user")
        input_pin = st.text_input("Enter 2-Digit Secret Access Pin:", type="password", key="login_pin")
        
        if st.button("Unlock Website & Enter 🚀"):
            if login_username not in users: st.error("❌ এই ইউজার আইডিটি পাওয়া যায়নি!")
            elif input_pin != config["master_pin"]: st.error("❌ ভুল এক্সেস পিন!")
            else:
                st.session_state.logged_in_user = login_username
                st.rerun()

# --- MAIN APP INTERFACE ---
else:
    current_user_id = st.session_state.logged_in_user
    
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f'<p class="main-title">⚡ অস্থির চালান PRO</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#38BDF8; font-weight:600;">Active Session: {current_user_id} (Authorized)</p>', unsafe_allow_html=True)
    with c2:
        if st.button("Log Out 🚪"):
            st.session_state.logged_in_user = None
            st.session_state.current_leads = []
            st.rerun()

    # --- SERPAPI & SCRAPER CORE ---
    def start_real_serp_hunting(search_query, status_box, table_placeholder, user_id):
        api_key = config.get("serp_api_key", "").strip()
        if not api_key:
            status_box.error("❌ এডমিন প্যানেলে SerpApi Key সেট করা নাই!")
            return []
            
        if user_id not in history: history[user_id] = []
        user_scraped_memory = set(history[user_id])
        
        status_box.info(f"🚀 Connecting to SerpApi Cloud Servers...")
        
        url = "https://serpapi.com/search"
        params = {"engine": "google_maps", "q": search_query, "type": "search", "api_key": api_key}
        
        leads = []
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            local_results = data.get("local_results", [])
            
            if not local_results:
                status_box.warning("⚠️ নতুন কোনো ডাটা পাওয়া যায়নি।")
                return []
                
            for idx, place in enumerate(local_results):
                place_id = place.get("data_id", place.get("title"))
                if place_id in user_scraped_memory: continue
                
                website = place.get("website", "N/A")
                phone = place.get("phone", "N/A")
                
                status_box.info(f"🔍 Scraped {idx+1}/{len(local_results)}: Hunting Email from website...")
                email = extract_email_from_website(website)
                
                leads.append({
                    "Client Name": place.get("title", "N/A"),
                    "Number": phone,
                    "Website": website,
                    "Email": email,
                    "Address": place.get("address", "N/A")
                })
                history[user_id].append(place_id)
                
                # Live rendering
                df_current = pd.DataFrame(leads)
                table_placeholder.dataframe(df_current, use_container_width=True)
                
            st.session_state.history_cache = history
            save_json_file(HISTORY_DB, history)
                
        except Exception as e:
            status_box.error(f"Error: {str(e)}")
            
        return leads

    # --- UI SEARCH PANEL ---
    search_keyword = st.text_input("Enter Niche & Location:", placeholder="e.g., Wedding Photographer in New York")
    if st.button("LAUNCH REAL-TIME MOVEMENT CORE 🚀"):
        if search_keyword:
            status_box = st.empty()
            table_placeholder = st.empty()
            results = start_real_serp_hunting(search_keyword, status_box, table_placeholder, current_user_id)
            if results:
                st.session_state.current_leads = results
                st.success(f"🔥 Successfully Fetched {len(results)} FRESH Leads with Email Hunter Enabled!")
            else:
                st.warning("🔄 কোনো নতুন ডাটা পাওয়া যায়নি!")

    # --- RENDER CURRENT LEADS TABLE ---
    if st.session_state.current_leads:
        st.markdown("### 📋 Found Leads Information")
        df_display = pd.DataFrame(st.session_state.current_leads)
        st.dataframe(df_display, use_container_width=True)
        
        # --- SMART AI-STYLE CAMPAIGN ENGINE ---
        st.markdown("---")
        st.markdown("<h2>⚡ Smart Auto-Template Sales Station</h2>", unsafe_allow_html=True)
        
        # প্রোফাইল ও অফার ডাটা ইনপুট বক্স
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            my_company = st.text_input("🏢 Your Company/Agency Name:", value="Reyadh Marketing Lab")
            my_role = st.text_input("👑 Your Designation/Role:", value="Founder")
        with col_inp2:
            my_services = st.text_input("🛠️ Services You Offer:", placeholder="e.g., Premium Photo & Video Editing Services")
            target_reason = st.text_input("🎯 Reason / Pain Point to Approach:", placeholder="e.g., spending too many sleepless nights editing thousands of wedding raw photos")

        # এসএমটিপি কানেকশন সুইচার
        st.markdown("<h4>📬 Dynamic SMTP Sender Details</h4>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            custom_sender = st.text_input("Sender Gmail Account:", placeholder="brand@gmail.com")
        with col_m2:
            custom_app_pass = st.text_input("Google App Password:", type="password", placeholder="16-digit secret code")
            
        st.markdown("<br>", unsafe_allow_html=True)
        campaign_subject = st.text_input("Cold Mail Email Subject:", value="Quick question regarding your photography post-production 📸")
        
        # ব্যাকগ্রাউন্ড টেমপ্লেট মেকার ফাংশন
        def build_dynamic_cold_mail(client_name, company, role, services, reason):
            template = f"Hello {client_name},\n\n" \
                       f"I hope you are doing well. I stumbled upon your business page on Google Maps and was highly impressed by your work!\n\n" \
                       f"I am writing to you because I noticed that you might be {reason}. " \
                       f"At {company}, we specialize in {services}, which helps businesses exactly like yours overcome this and skyrocket their revenue.\n\n" \
                       f"Would you be open to a short 5-minute call this week to see how we can bring more premium clients to your business?\n\n" \
                       f"Best regards,\n" \
                       f"{role} | {company}"
            return template

        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            if st.button("🚀 AUTO-GENERATE & BLAST ALL COLD MAILS"):
                if not custom_sender.strip() or not custom_app_pass.strip():
                    st.error("❌ ইমেইল ব্লাস্ট করার আগে উপরে আপনার জিমেইল এবং অ্যাপ পাসওয়ার্ড দিন!")
                elif not my_services or not target_reason:
                    st.error("❌ আপনার সার্ভিস এবং আপ্রোচ করার কারণ (Pain Point) ফাঁকা রাখা যাবে না!")
                else:
                    success_count = 0
                    try:
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.starttls()
                        server.login(custom_sender.strip(), custom_app_pass.strip())
                        
                        for lead in st.session_state.current_leads:
                            to_email = lead["Email"]
                            # ইমেইল ফাঁকা না থাকলে এবং ভুয়া ইমেইল না হলেই কেবল পাঠানো হবে
                            if to_email != "N/A" and "@" in to_email:
                                personal_msg = build_dynamic_cold_mail(
                                    client_name=lead["Client Name"],
                                    company=my_company,
                                    role=my_role,
                                    services=my_services,
                                    reason=target_reason
                                )
                                
                                msg = MIMEMultipart()
                                msg["From"] = custom_sender
                                msg["To"] = to_email
                                msg["Subject"] = campaign_subject
                                msg.attach(MIMEText(personal_msg, "plain", "utf-8"))
                                
                                server.sendmail(custom_sender, to_email, msg.as_string())
                                success_count += 1
                                
                        server.quit()
                        st.success(f"🎯 Boom! {custom_sender} থেকে {success_count} জন ক্লায়েন্টের নিজস্ব নাম ও পেইন পয়েন্ট বসিয়ে আলাদা আলাদা মেইল অটো-ব্লাস্ট করা হয়েছে!")
                    except Exception as e:
                        st.error(f"Gmail System Error: {str(e)}")
                        
        with col_c2:
            st.markdown("### 💬 WhatsApp Smart Links (With Auto Text)")
            st.write("নিচের লিংকে ক্লিক করলেই ওই ক্লায়েন্টের নাম ও আপনার কাস্টম অফার সহ হোয়াটসঅ্যাপ চ্যাট ওপেন হবে:")
            for lead in st.session_state.current_leads:
                num = lead["Number"]
                if num != "N/A":
                    clean_num = re.sub(r'\D', '', num)
                    wa_msg = build_dynamic_cold_mail(
                        client_name=lead["Client Name"],
                        company=my_company,
                        role=my_role,
                        services=my_services,
                        reason=target_reason
                    )
                    encoded_msg = urllib.parse.quote(wa_msg)
                    wa_link = f"https://wa.me/{clean_num}?text={encoded_msg}"
                    st.markdown(f"👉 [{lead['Client Name']} - Send WA Pitch]({wa_link})")

# --- REYADH BHAI's GOD-MODE ADMIN PANEL ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Reyadh Bhai's Secret Control Room"):
    admin_auth = st.text_input("Enter Secret Admin Password:", type="password", key="admin_auth_pass")
    if admin_auth == config["admin_pass"]:
        st.success("Welcome Back, Owner!")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 👥 Manage Active Users")
            current_users = list(users.keys())
            if not current_users: st.info("কোনো ইউজার নাই।")
            else:
                for u in current_users:
                    col_u, col_b = st.columns([3, 1])
                    col_u.text(f"👤 User: {u}")
                    if col_b.button("Delete User ❌", key=f"del_{u}"):
                        del users[u]
                        st.session_state.users_cache = users
                        save_json_file(USER_DB, users)
                        st.success(f"User '{u}' deleted!"); st.rerun()
        with c2:
            st.markdown("### ⚙️ System Config")
            new_key = st.text_input("Paste Your SerpApi Key here:", type="password", value=config.get("serp_api_key",""))
            if st.button("Save API Key 💾"):
                config["serp_api_key"] = new_key
                st.session_state.config_cache = config
                save_json_file(CONFIG_FILE, config)
                st.success("💥 SerpApi Key সেভড!"); st.rerun()
                    
    elif admin_auth != "": st.error("ভুল পাসওয়ার্ড!")

st.markdown('<div class="footer">Osthir Chalan Engine v11.0 | Handcrafted by <span>MD Reyadh</span></div>', unsafe_allow_html=True)
