import streamlit as st
import os
import json
import requests
import pandas as pd
import re
import smtplib
import time
import datetime
import urllib.parse
import streamlit.components.v1 as components
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- DATABASE LAYER (100% DATA RETENTION) ---
USER_DB = "users_db.json"
CONFIG_FILE = "system_config.json"
HISTORY_DB = "users_history_memory.json"
CHAT_DB = "system_chat_memory.json"

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f: return json.load(f)
        except: return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

if "users_cache" not in st.session_state: st.session_state.users_cache = load_json_file(USER_DB, {})
if "config_cache" not in st.session_state: st.session_state.config_cache = load_json_file(CONFIG_FILE, {"master_pin": "69", "admin_pass": "reyadh123", "notice_text": "স্বাগতম অস্থির চালান PRO v29.0! অ্যান্টি-ডুপ্লিকেট ইঞ্জিন লাইভ: ইউজাররা কখনো পুরনো বা একই স্ক্র্যাপড ডাটা পুনরায় দেখতে পাবেন না।"})
if "history_cache" not in st.session_state: st.session_state.history_cache = load_json_file(HISTORY_DB, [])
if "chat_cache" not in st.session_state: st.session_state.chat_cache = load_json_file(CHAT_DB, [])

users = st.session_state.users_cache
config = st.session_state.config_cache
history_logs = st.session_state.history_cache
chat_messages = st.session_state.chat_cache

st.set_page_config(page_title="অস্থির চালান PRO v29.0", page_icon="🛡️", layout="wide")

# CSS STYLING
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', 'Hind Siliguri', sans-serif !important; background-color: #0B0F19 !important; color: #F1F5F9 !important; }
    .main-title { font-family: 'Hind Siliguri', sans-serif !important; font-size: 40px !important; font-weight: 700 !important; color: #F8FAFC !important; }
    .notice-board { background-color: #111827; border-left: 4px solid #EC4899; padding: 15px; border-radius: 8px; margin-bottom: 25px; }
    .section-container { background-color: #111827; border: 1px solid #1F2937; padding: 20px; border-radius: 12px; margin-top: 15px; }
    .platform-card { background: #1E293B; border: 1px solid #334155; padding: 14px; border-radius: 8px; margin-bottom: 10px; }
    .chat-box { height: 280px; overflow-y: auto; background: #111827; border: 1px solid #1F2937; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .msg-incoming { background: #1E293B; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; }
    .msg-outgoing { background: #EC4899; color: white; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; margin-left: auto; width: fit-content; max-width: 80%; text-align: right; }
    .alert-card { background: #7F1D1D; border-left: 5px solid #EF4444; padding: 12px; border-radius: 6px; margin: 10px 0; color: #FCA5A5; font-weight: bold; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0B0B12; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #1F2937; z-index: 99; }
    </style>
""", unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "current_leads" not in st.session_state: st.session_state.current_leads = []
if "instagram_hunting_leads" not in st.session_state: st.session_state.instagram_hunting_leads = []
if "email_sent_counter" not in st.session_state: st.session_state.email_sent_counter = 0
if "connected_email" not in st.session_state: st.session_state.connected_email = ""

# --- FREE EXTRACTION LOGIC ---
def free_html_email_extractor(url):
    if not url or url == "N/A": return "N/A"
    try:
        if not url.startswith("http"): url = "http://" + url
        res = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        emails = re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z0-9.\-_]+', res.text)
        for e in emails:
            if not any(kw in e.lower() for kw in ['user@', 'email@', 'example']): return e
    except: pass
    return "N/A"

def instagram_keyword_scout(keyword, user_id, limit=20):
    try:
        # ইউজারের আগের স্ক্র্যাপ করা ডাটাবেস ইউনিক হিস্টোরি চেক
        scraped_before = set([log.get("identifier") for log in history_logs if log.get("user") == user_id and log.get("type") == "Instagram Hunter"])
        
        search_q = f'site:instagram.com "{keyword}" "biography"'
        res = requests.post("https://html.duckduckgo.com/html/", data={'q': search_q}, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        raw_links = re.findall(r'href="(https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_\.]+)"', res.text)
        snippets = re.findall(r'<td class="result-snippet">([\s\S]*?)</td>', res.text)
        
        found_leads = []
        for idx, link in enumerate(list(set(raw_links))):
            if len(found_leads) >= limit: break
            username = link.split("instagram.com/")[-1].replace("/", "")
            if username in ['p', 'explore', 'developer'] or link in scraped_before: continue # ম্যাচ করলে স্কিপ
            
            snippet_text = re.sub('<[^<]+?>', '', snippets[idx]) if idx < len(snippets) else "Professional Bio Data"
            emails_found = re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z0-9.\-_]+', snippet_text)
            extracted_email = emails_found[0] if emails_found else "N/A"
            
            found_leads.append({"Client Name": username.upper(), "Website": f"https://instagram.com/{username}", "Email": extracted_email, "WhatsApp Number": "N/A", "Instagram Profile": link, "Bio Snippet": snippet_text.strip()})
        return found_leads
    except: return []

# --- GATEWAY AUTH ---
if st.session_state.logged_in_user is None:
    st.markdown('<p class="main-title">অস্থির চালান PRO 🛡️</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice-board">📢 <b>সিস্টেম নোটিশ বোর্ড:</b><br>{config.get("notice_text", "")}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4>নতুন অ্যাকাউন্ট রেজিস্টার</h4>", unsafe_allow_html=True)
        new_username = st.text_input("ইউনিক ইউজার আইডি (User ID):", key="reg_user")
        if st.button("অ্যাকাউন্ট তৈরি করুন"):
            if new_username.strip() and new_username not in users:
                users[new_username] = {"status": "Active", "last_seen": time.time()}
                save_json_file(USER_DB, users); st.success("✅ অ্যাকাউন্ট তৈরি হয়েছে!")
    with col2:
        st.markdown("<h4>নিরাপদ গেটওয়ে লগইন</h4>", unsafe_allow_html=True)
        login_username = st.text_input("ইউজার আইডি (User ID):", key="login_user")
        input_pin = st.text_input("২-ডিジット পিন:", type="password", key="login_pin", max_chars=2)
        if st.button("কোর ড্যাশবোর্ড আনলক করুন 🚀"):
            if login_username in users and input_pin == config["master_pin"]:
                users[login_username]["last_seen"] = time.time()
                save_json_file(USER_DB, users)
                st.session_state.logged_in_user = login_username; st.rerun()
            else: st.error("❌ ভুল ক্রেডেনশিয়াল!")
else:
    current_user_id = st.session_state.logged_in_user
    if current_user_id in users:
        users[current_user_id]["last_seen"] = time.time()
        save_json_file(USER_DB, users)
        
    c1, c2 = st.columns([6, 1])
    c1.markdown(f'<p class="main-title">অস্থির চালান PRO <span style="font-size:16px; color:#EC4899;">// NODE: {current_user_id.upper()}</span></p>', unsafe_allow_html=True)
    if c2.button("লগআউট 🚪"): st.session_state.logged_in_user = None; st.rerun()

    engine_tab1, engine_tab2, engine_tab3, engine_tab4 = st.tabs(["📍 Google Maps Scraper (Max 100)", "📸 Instagram Hunter (Max 20)", "📊 Campaign History & Follow-up", "💬 Chat & Video Call Room"])

    # --- TAB 1: GOOGLE MAPS ENGINE WITH ANTI-DUPLICATE ---
    with engine_tab1:
        st.markdown("<h4 style='color:#38BDF8;'>📍 গুগল ম্যাপস ডাটা ক্রলার (১০০% ইউনিক ফিল্টারিং সিস্টেম)</h4>", unsafe_allow_html=True)
        search_keyword = st.text_input("কীওয়ার্ড এবং লোকেশন দিন:")
        if st.button("ম্যাপস ক্রলার ইঞ্জিন চালু করুন 🚀", key="maps_btn"):
            if search_keyword:
                status_box = st.empty().info("ম্যাপস স্ক্যান করা হচ্ছে... আপনার পুরনো ডেটাগুলো অটো ফিল্টার করা হচ্ছে...")
                
                # ইউজারের আগের স্ক্র্যাপ করা ম্যাপস লিড ফিল্টার সেট
                scraped_maps_before = set([log.get("identifier") for log in history_logs if log.get("user") == current_user_id and log.get("type") == "Google Maps"])
                
                map_url = f"https://www.google.com/maps/search/{urllib.parse.quote(search_keyword)}?hl=en"
                res = requests.get(map_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
                potential_websites = re.findall(r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-z]{2,6}', res.text)
                clean_websites = list(set([w for w in potential_websites if not any(x in w for x in ["google", "gstatic", "schema", "facebook", "instagram"])]))
                
                leads = []
                idx_counter = 1
                for web_url in clean_websites:
                    if len(leads) >= 100: break
                    if web_url in scraped_maps_before: continue # যদি আগে স্ক্র্যাপ করে থাকে, স্কিপ!
                    
                    email = free_html_email_extractor(web_url)
                    leads.append({"Client Name": f"Maps Client {idx_counter}", "Website": web_url, "Email": email, "WhatsApp Number": "N/A", "Instagram Profile": "N/A"})
                    
                    # গ্লোবাল হিস্টোরিতে ইউনিক আইডি হিসেবে ওয়েবসাইটটি ঢুকিয়ে দেওয়া হচ্ছে
                    log_entry = {"user": current_user_id, "date": str(datetime.date.today()), "time": datetime.datetime.now().strftime("%H:%M:%S"), "keyword": search_keyword, "type": "Google Maps", "identifier": web_url}
                    history_logs.append(log_entry)
                    idx_counter += 1
                
                save_json_file(HISTORY_DB, history_logs)
                st.session_state.current_leads = leads
                
                if leads:
                    st.dataframe(pd.DataFrame(leads), use_container_width=True)
                    status_box.success(f"সাফল্যের সাথে {len(leads)} টি সম্পূর্ণ নতুন ও ফ্রেশ ম্যাপস লিড সেভ করা হয়েছে!")
                else:
                    status_box.warning("⚠️ এই কিওয়ার্ডে নতুন কোনো ইউনিক লিড পাওয়া যায়নি! সব পুরনো ডাটা ফিল্টার করা হয়েছে।")

    # --- TAB 2: INSTAGRAM HUNTER WITH ANTI-DUPLICATE ---
    with engine_tab2:
        st.markdown("<h4 style='color:#EC4899;'>📸 ইনস্টাগ্রাম ডাইরেক্ট নিশ-বেসড ক্রলার (১০০% ইউনিক ফিল্টারিং সিস্টেম)</h4>", unsafe_allow_html=True)
        now_ts = time.time()
        last_scrap_key = f"last_ig_scrap_{current_user_id}"
        last_scrap_time = st.session_state.get(last_scrap_key, 0)
        cooldown_period = 300 
        elapsed = now_ts - last_scrap_time
        
        if elapsed < cooldown_period:
            remaining = int(cooldown_period - elapsed)
            mins, secs = divmod(remaining, 60)
            st.markdown(f'<div class="alert-card">⚠️ ইনস্টাগ্রাম সিকিউরিটি লক! ২০টি স্ক্র্যাপ কমপ্লিট হয়েছে। অ্যাকাউন্ট সেফ রাখতে লাইভ কুলডাউন হচ্ছে: {mins:02d}:{secs:02d} মিনিট পর আবার ওপেন হবে।</div>', unsafe_allow_html=True)
            st.button("ইনস্টাগ্রাম লাইভ হান্ট শুরু করুন 🔥", disabled=True, key="ig_disabled")
        else:
            ig_keyword = st.text_input("ইনস্টাগ্রাম টার্গেট নিশ/কীওয়ার্ড লিখুন:")
            if st.button("ইনস্টাগ্রাম লাইভ হান্ট শুরু করুন 🔥", key="ig_active_btn"):
                if ig_keyword:
                    st.session_state[last_scrap_key] = time.time()
                    ig_leads = instagram_keyword_scout(ig_keyword, current_user_id, limit=20)
                    
                    if ig_leads:
                        st.session_state.instagram_hunting_leads = ig_leads
                        st.dataframe(pd.DataFrame(ig_leads), use_container_width=True)
                        
                        # প্রতিটা নতুন লিডের প্রোফাইল ইউনিক আইডেন্টিফায়ার হিসেবে মেমোরিতে সেভ হচ্ছে
                        for lead in ig_leads:
                            history_logs.append({"user": current_user_id, "date": str(datetime.date.today()), "time": datetime.datetime.now().strftime("%H:%M:%S"), "keyword": ig_keyword, "type": "Instagram Hunter", "identifier": lead["Instagram Profile"]})
                        save_json_file(HISTORY_DB, history_logs)
                        st.success("২০টি সম্পূর্ণ ফ্রেশ ইনস্টাগ্রাম লিড ক্রল সম্পন্ন! পুরনো সব ডাটা বাদ দেওয়া হয়েছে।")
                        st.rerun()
                    else:
                        st.warning("⚠️ নতুন কোনো ইউনিক আইডি পাওয়া যায়নি। একটু ভিন্ন কিওয়ার্ড দিয়ে ট্রাই করুন ভাই।")

    # --- TAB 3: CAMPAIGN LOGS & FOLLOW-UP ---
    with engine_tab3:
        st.markdown("<h4>📋 অল-টাইম অ্যাকাউন্ট অ্যাক্টিভিটি হিস্টোরি ও ফলো-আপ ট্র্যাকিং ডাটাবেস</h4>", unsafe_allow_html=True)
        user_history = [log for log in history_logs if log.get("user") == current_user_id]
        if user_history: 
            df_hist = pd.DataFrame(user_history)
            # ক্লিন ডিসপ্লের জন্য ইউজার ড্যাশবোর্ডে রেন্ডার
            st.dataframe(df_hist[["date", "time", "keyword", "type", "identifier"]].rename(columns={"identifier": "Scraped Unique Link/Target"}), use_container_width=True)
        else: 
            st.info("কোনো ডাটা মেমোরি এখনো রেকর্ড হয়নি।")

    # --- TAB 4: REAL-TIME CHAT & VIDEO CALL ENGINE ---
    with engine_tab4:
        st.markdown("<h3 style='color:#EC4899;'>💬 মেম্বার টু মেম্বার লাইভ চ্যাট ও রিয়েল-টাইম ভিডিও কল রূম</h3>", unsafe_allow_html=True)
        st.markdown("##### 🟢 অনলাইন মেম্বার ট্র্যাকিং")
        member_cols = st.columns(len(users) if users else 1)
        for idx, (m_id, m_data) in enumerate(users.items()):
            last_seen_ts = m_data.get("last_seen", 0)
            is_online = (time.time() - last_seen_ts) < 60
            status_dot = "🟢 Online" if is_online else f"🔴 Offline ({datetime.datetime.fromtimestamp(last_seen_ts).strftime('%I:%M %p')})"
            if idx < len(member_cols): member_cols[idx].metric(label=f"User: {m_id.upper()}", value=m_id.upper(), delta=status_dot)
        
        c_left, c_right = st.columns([2, 2])
        with c_left:
            st.markdown("##### 📝 ইনস্ট্যান্ট চ্যাট মেমোরি")
            chat_html = '<div class="chat-box">'
            for msg in chat_messages:
                msg_class = "msg-outgoing" if msg["sender"] == current_user_id else "msg-incoming"
                chat_html += f'<div class="{msg_class}"><b>{msg["sender"].upper()}:</b> {msg["text"]}<br><small style="font-size:9px;opacity:0.7;">{msg["time"]}</small></div>'
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
            
            with st.form("chat_form", clear_on_submit=True):
                typed_msg = st.text_input("মেসেজ লিখুন:", key="msg_inp")
                if st.form_submit_button("মেসেজ পাঠান ✉️"):
                    if typed_msg.strip():
                        chat_messages.append({"sender": current_user_id, "text": typed_msg.strip(), "time": datetime.datetime.now().strftime("%I:%M %p")})
                        save_json_file(CHAT_DB, chat_messages); st.rerun()
                        
        with c_right:
            st.markdown("##### 📹 WebRTC স্ক্রিন শেয়ার ভিডিও কল ইন্টারফেস")
            components.html("""
            <div style="background:#111827; border:1px solid #1F2937; padding:20px; border-radius:10px; text-align:center;">
                <video id="lVid" autoplay playsinline muted style="width:45%; background:#000; border-radius:8px; margin-right:5%;"></video>
                <video id="rVid" autoplay playsinline style="width:45%; background:#000; border-radius:8px;"></video><br><br>
                <button style="background:#EC4899; color:white; border:none; padding:10px 15px; border-radius:6px; font-weight:bold; cursor:pointer;" onclick="init()">📹 ক্যামেরা অন</button>
                <button style="background:#38BDF8; color:black; border:none; padding:10px 15px; border-radius:6px; font-weight:bold; cursor:pointer; margin-left:10px;" onclick="scr()">🖥️ স্ক্রিন শেয়ার</button>
            </div>
            <script>
                async function init(){let s=await navigator.mediaDevices.getUserMedia({video:true,audio:true});document.getElementById('lVid').srcObject=s;}
                async function scr(){let s=await navigator.mediaDevices.getDisplayMedia({video:true});document.getElementById('lVid').srcObject=s;}
            </script>
            """, height=260)

    # --- MARKETING HUBS (SHARED ACTIVE DATASET) ---
    active_dataset = st.session_state.instagram_hunting_leads if st.session_state.instagram_hunting_leads else st.session_state.current_leads

    if active_dataset:
        st.markdown("### 💥 মাল্টি-চ্যানেল营销 কাস্টমাইজড কন্ট্রোল হাব")
        col_sec1, col_sec2, col_sec3 = st.columns(3)
        if "active_tab" not in st.session_state: st.session_state.active_tab = "email"
        if col_sec1.button("📧 কোল্ড ইমেইল প্যানেল", use_container_width=True): st.session_state.active_tab = "email"
        if col_sec2.button("🟢 হোয়াটসঅ্যাপ প্যানেল", use_container_width=True): st.session_state.active_tab = "whatsapp"
        if col_sec3.button("📸 ইনস্টাগ্রাম ডাইরেক্ট প্যানেল", use_container_width=True): st.session_state.active_tab = "instagram"

        # COLD EMAIL PANEL
        if st.session_state.active_tab == "email":
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown(f"📊 **বর্তমান মেলিং সেশন ট্র্যাকার:** `{st.session_state.email_sent_counter} / 100`")
            
            if st.session_state.email_sent_counter >= 100:
                st.markdown(f'<div class="alert-card">🛑 সতর্কবার্তা: {st.session_state.connected_email} অ্যাকাউন্ট থেকে ১০০টি কোল্ড মেইল পাঠানো সম্পন্ন হয়েছে! দয়া করে একটি নতুন জিমেইল অ্যাকাউন্ট কানেক্ট করুন।</div>', unsafe_allow_html=True)
            
            ce1, ce2 = st.columns(2)
            e_sender = ce1.text_input("আপনার জিমেইল অ্যাকাউন্ট:", placeholder="name@gmail.com", key="m_sender")
            e_pass = ce1.text_input("জিমেইল অ্যাপ পাসওয়ার্ড:", type="password", key="m_pass")
            e_subject = ce2.text_input("মেইল সাবজেক্ট:", value="Business Growth Proposal", key="m_subj")
            email_pitch = st.text_area("মেইল বডি ({client_name}):", value="Hi {client_name},\n\nLoved your profile. Let's collaborate.\n\nBest,\nReyadh", key="m_pitch")
            
            if e_sender and e_sender != st.session_state.connected_email:
                st.session_state.connected_email = e_sender
                st.session_state.email_sent_counter = 0 
            
            if st.session_state.email_sent_counter >= 100:
                st.button("🚀 ভ্যালিড ইমেইলগুলোতে মুহূর্তে অটো-মেইল পাঠান", disabled=True, key="mail_dis")
            else:
                if st.button("🚀 ভ্যালিড ইমেইলগুলোতে মুহূর্তে অটো-মেইল পাঠান", key="mail_act"):
                    if e_sender and e_pass:
                        sent = 0
                        try:
                            server = smtplib.SMTP("smtp.gmail.com", 587)
                            server.starttls(); server.login(e_sender.strip(), e_pass.strip())
                            for lead in active_dataset:
                                if st.session_state.email_sent_counter >= 100: break
                                if lead["Email"] != "N/A":
                                    msg = MIMEMultipart()
                                    msg["From"] = e_sender; msg["To"] = lead["Email"]; msg["Subject"] = e_subject
                                    msg.attach(MIMEText(email_pitch.replace("{client_name}", lead["Client Name"]), "plain", "utf-8"))
                                    server.sendmail(e_sender, lead["Email"], msg.as_string())
                                    sent += 1; st.session_state.email_sent_counter += 1
                            server.quit()
                            st.success(f"সফলভাবে এই ব্যাচে {sent} টি কাস্টমাইজড মেইল সেন্ট হয়েছে!")
                            st.rerun()
                        except Exception as e: st.error(f"Error: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

        # WHATSAPP PANEL
        elif st.session_state.active_tab == "whatsapp":
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            wa_pitch = st.text_area("হোয়াটসঅ্যাপ পিচ:", value="Hey {client_name}, saw your profile. Let's connect!")
            for lead in active_dataset:
                num = lead["WhatsApp Number"]
                if num != "N/A":
                    wa_url = f"https://api.whatsapp.com/send?phone={re.sub(r'\D', '', num)}&text={urllib.parse.quote(wa_pitch.replace('{client_name}', lead['Client Name']))}"
                    st.markdown(f'<div class="platform-card">📱 <b>{lead["Client Name"]}</b><br><a href="{wa_url}" target="_blank" style="color:#22C55E; font-weight:bold; text-decoration:none;">⚡ ১-ক্লিকে চ্যাট ও কাস্টম মেসেজ পাঠান</a></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # INSTAGRAM CUSTOM PANEL
        elif st.session_state.active_tab == "instagram":
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            ig_pitch = st.text_area("ইনস্টাগ্রাম কাস্টম পিচ:", value="Hey {client_name}! Checked your profile. Can I drop a blueprint here?")
            for lead in active_dataset:
                ig_link = lead["Instagram Profile"]
                if ig_link != "N/A":
                    u_name = ig_link.split("instagram.com/")[-1].replace("/", "")
                    st.markdown(f"""
                    <div class="platform-card" style="border-left: 4px solid #EC4899;">
                        📸 <b>{lead['Client Name']}</b> (@{u_name})<br>
                        <p style='color:#94A3B8; font-size:13px; margin:5px 0;'>কপি করুন: <code style='color:#EC4899;'>{ig_pitch.replace('{client_name}', lead['Client Name'])}</code></p>
                        <a href="{ig_link}" target="_blank" style="display:inline-block; background:#1E293B; border:1px solid #EC4899; color:#EC4899 !important; padding:5px 10px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:bold;">🔗 ১-ক্লিকে ইনবক্স ও সেন্ড</a>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# SECRET CONTROL PANEL
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Reyadh Bhai's Secret Control Room"):
    if st.text_input("Enter Admin Password:", type="password", key="admin_key") == config["admin_pass"]:
        updated_notice = st.text_area("নোটিশ বোর্ড এডিট করুন:", value=config.get("notice_text", ""))
        if st.button("আপডেট নোটিশ"):
            config["notice_text"] = updated_notice; save_json_file(CONFIG_FILE, config)
            st.success("নোটিশ লাইভ আপডেট হয়েছে!"); st.rerun()

st.markdown('<div class="footer">অস্থির চালান ড্যাশবোর্ড v29.0 | Developed by <span>MD Reyadh</span></div>', unsafe_allow_html=True)
