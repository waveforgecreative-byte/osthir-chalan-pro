import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# ১. ক্লায়েন্ট ডাটা (উদাহরণ হিসেবে দেওয়া, আপনি চাইলে Excel ফাইলও লোড করতে পারেন)
# excel_file = pd.read_excel('clients.xlsx')
data = {
    'Name': ['Rahim', 'Karim', 'John'],
    'Email': ['rahim@example.com', 'karim@example.com', 'john@example.com']
}
df = pd.DataFrame(data)

# ২. আপনার ইমেইল কনফিগারেশন
YOUR_EMAIL = "your_email@gmail.com"
YOUR_PASSWORD = "your_app_password"  # জিমেইলের App Password ব্যবহার করবেন

# ৩. মেইল টাইপ সিলেক্ট করুন (Cold Mail নাকি Follow-up)
mail_type = input("Choose type (1 for Cold Mail, 2 for Follow-up): ")
custom_choice = input("Do you want to write a Custom Message? (yes/no): ").lower()

# ৪. মেসেজ টেমপ্লেট ডিফাইন করা
if custom_choice == 'yes':
    print("\n--- Custom Message লিখুন (নামের জায়গায় {name} ব্যবহার করুন) ---")
    subject = input("Subject: ")
    body_template = input("Body: ")
else:
    if mail_type == '1':
        subject = "Business Proposal for Your Company"
        body_template = "Hello {name},\n\nI hope you are doing well. I saw your profile and wanted to reach out regarding our services..."
    else:
        subject = "Following up on my previous email"
        body_template = "Hello {name},\n\nJust wanted to follow up and see if you had a chance to look at my previous email..."

# ৫. মেইল পাঠানোর মেইন লুপ
try:
    # Gmail SMTP সার্ভারের সাথে কানেক্ট করা
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(YOUR_EMAIL, YOUR_PASSWORD)
    
    for index, row in df.iterrows():
        client_name = row['Name']
        client_email = row['Email']
        
        # নামের জায়গায় অটোমেটিক ক্লায়েন্টের নাম বসিয়ে দেবে ({name} রিপ্লেস হবে)
        custom_body = body_template.format(name=client_name)
        
        # ইমেইল স্ট্রাকচার তৈরি
        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = client_email
        msg['Subject'] = subject
        msg.attach(MIMEText(custom_body, 'plain'))
        
        # মেইল সেন্ড করা
        server.send_message(msg)
        print(f"✅ Successfully sent to {client_name} ({client_email})")
        
        # অ্যান্টি-ব্যান (Anti-Ban) প্রোটেকশন: প্রতি মেইলের মাঝে ৫ সেকেন্ড গ্যাপ
        time.sleep(5)
        
    print("\n🎉 All emails sent successfully!")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    server.quit()
