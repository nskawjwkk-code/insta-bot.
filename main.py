import os
import time
import json
import threading
import datetime
from instagrapi import Client
from flask import Flask

# ==========================================
# 1. سيرفر Flask (باش البوت ما يطفاش في Render)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "BOT V8.0 ONLINE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask, daemon=True).start()

# ==========================================
# 2. إعدادات الحساب
# ==========================================
USERNAME = "zalsj.20"
PASSWORD = os.getenv("IG_PASSWORD", "Abdou20")

# ⚠️ الأدمينة
ADMINS = ["bat.2541453"]

# ==========================================
# 3. تشغيل البوت (مع Session)
# ==========================================
cl = Client()
cl.delay_range = [1, 3]

SESSION_FILE = "session.json"

try:
    # 1. إذا كان ملف Session موجود، نستعملوه
    if os.path.exists(SESSION_FILE):
        print("📂 راهو يقرا الـ Session المحفوظة...")
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        print(f"✅ تم تسجيل الدخول من الـ Session: {USERNAME}")
    else:
        # 2. أول مرة: نسجل دخول عادي
        print("🔑 أول مرة: راهو يسجل دخول جديد...")
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print(f"✅ تم تسجيل الدخول وحفظ الـ Session: {USERNAME}")
except Exception as e:
    print(f"❌ فشل تسجيل الدخول: {e}")
    print("⚠️ ملاحظة: إذا كان الخطأ 'missing code_entry context_data'، معناها الحساب محبوس من إنستغرام، ولازم Session.")
    exit()

# ==========================================
# 4. حفظ الإعدادات
# ==========================================
SETTINGS_FILE = "bot_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "protected_groups": {},
        "welcome_on": {},
        "group_locked": {},
        "spam_stop": False
    }

def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ فشل حفظ الإعدادات: {e}")

settings = load_settings()

# ==========================================
# 5. دوال مساعدة
# ==========================================
def send(tid, text):
    try:
        cl.direct_send(text, thread_ids=[tid])
    except Exception as e:
        print(f"⚠️ خطأ إرسال: {e}")

def get_username(user_id):
    try:
        return cl.user_info(user_id).username
    except:
        return "مجهول"

# ==========================================
# 6. الردود التلقائية والأوامر
# ==========================================
AUTO_REPLIES = {
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته 🌹",
    "سلام": "وعليكم السلام 🌸",
    "صباح الخير": "صباح النور ☀️",
    "مساء الخير": "مساء النور 🌙",
    "شكرا": "العفو 🌹",
    "بارك الله فيك": "وفيك بارك الله 🤲",
    "كيف الحال": "الحمد لله، راك لاباس؟ 😊",
}

HELP_TEXT = """
╭─━━━━━━━━━━━━━─╮
   🤖 **BOT V8.0** 🤖
╰─━━━━━━━━━━━━━─╯

📌 **للجميع:**
• السلام عليكم / سلام
• صباح الخير / مساء الخير
• شكرا / بارك الله فيك
• اوامر

⚙️ **للأدمينة فقط:**
• طرد (بالرد)
• كنية [الاسم]
• سبام [العدد]
• احبس
• قفل / فتح
• ترحيب on/off
• حماية on/off
• حالة
"""

def handle(text, thread_id, sender, sender_id, reply_user=None, reply_user_id=None):
    low = text.strip().lower()
    original = text.strip()

    # ====== الردود التلقائية ======
    for key, reply in AUTO_REPLIES.items():
        if low == key.lower():
            send(thread_id, reply)
            return

    # ====== أوامر عامة ======
    if low in ["اوامر", "!هيلب", "help"]:
        send(thread_id, HELP_TEXT)
        return

    # ====== من هنا، الأوامر للأدمينة فقط ======
    if sender not in ADMINS:
        return

    if low == "طرد":
        if reply_user_id:
            try:
                cl.direct_thread_remove_members(thread_id, [reply_user_id])
                send(thread_id, f"🚪 تم طرد @{reply_user}")
            except Exception as e:
                send(thread_id, f"⚠️ ما قدرتش نطردو: {e}")
        else:
            send(thread_id, "❌ لازم ترد على رسالة العضو")
        return

    if low.startswith("كنية"):
        new_name = original[4:].strip()
        if not new_name:
            send(thread_id, "❌ اكتب: كنية الاسم الجديد")
            return
        try:
            cl.direct_thread_update_title(thread_id, new_name)
            send(thread_id, f"✅ تم تغيير الكنية إلى: {new_name}")
        except Exception as e:
            send(thread_id, f"⚠️ فشل التغيير: {e}")
        return

    if low.startswith("سبام"):
        parts = low.split()
        num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 3
        num = min(num, 10)
        settings["spam_stop"] = False
        save_settings(settings)
        send(thread_id, f"💥 بدء السبام ({num} رسائل)...")
        for i in range(num):
            if settings.get("spam_stop"):
                send(thread_id, "🛑 تم إيقاف السبام")
                break
            send(thread_id, f"💥 رسالة {i+1}/{num}")
            time.sleep(2)
        return

    if low == "احبس":
        settings["spam_stop"] = True
        save_settings(settings)
        send(thread_id, "🛑 تم إيقاف السبام")
        return

    if low == "قفل":
        settings["group_locked"][thread_id] = True
        save_settings(settings)
        send(thread_id, "🔒 تم قفل القروب")
        return

    if low == "فتح":
        settings["group_locked"][thread_id] = False
        save_settings(settings)
        send(thread_id, "🔓 تم فتح القروب")
        return

    if low == "ترحيب on":
        settings["welcome_on"][thread_id] = True
        save_settings(settings)
        send(thread_id, "🔔 تم تفعيل الترحيب")
        return

    if low == "ترحيب off":
        settings["welcome_on"][thread_id] = False
        save_settings(settings)
        send(thread_id, "🔕 تم إيقاف الترحيب")
        return

    if low == "حماية on":
        try:
            thread = cl.direct_thread(thread_id)
            settings["protected_groups"][thread_id] = thread.thread_title
            save_settings(settings)
            send(thread_id, "🛡️ تم تفعيل حماية اسم القروب")
        except Exception as e:
            send(thread_id, f"⚠️ فشل: {e}")
        return

    if low == "حماية off":
        if thread_id in settings["protected_groups"]:
            del settings["protected_groups"][thread_id]
            save_settings(settings)
        send(thread_id, "🔓 تم إيقاف الحماية")
        return

    if low == "حالة":
        send(thread_id, f"""
📊 **حالة البوت:**
• حماية: {'✅' if thread_id in settings['protected_groups'] else '❌'}
• ترحيب: {'✅' if settings['welcome_on'].get(thread_id) else '❌'}
• قفل: {'✅' if settings['group_locked'].get(thread_id) else '❌'}
• الوقت: {datetime.datetime.now().strftime('%H:%M:%S')}
        """)
        return

# ==========================================
# 7. لوب المراقبة
# ==========================================
print("🚀 البوت V8.0 راهو خدام...")
last_seen = {}

while True:
    try:
        threads = cl.direct_threads(5)
        for thread in threads:
            if not thread.messages:
                continue

            if thread.id in settings["protected_groups"]:
                original_name = settings["protected_groups"][thread.id]
                if thread.thread_title != original_name:
                    try:
                        cl.direct_thread_update_title(thread.id, original_name)
                        print(f"🛡️ رجعنا اسم القروب: {original_name}")
                    except:
                        pass

            m = thread.messages[0]
            if m.user_id == cl.user_id:
                continue
            if last_seen.get(thread.id) == m.id:
                continue
            last_seen[thread.id] = m.id

            if not m.text:
                continue

            sender = get_username(m.user_id)
            sender_id = m.user_id

            reply_user = None
            reply_user_id = None
            if m.reply_to_message and m.reply_to_message.user_id != cl.user_id:
                reply_user = get_username(m.reply_to_message.user_id)
                reply_user_id = m.reply_to_message.user_id

            if settings["group_locked"].get(thread.id) and sender not in ADMINS:
                try:
                    cl.direct_message_delete(thread.id, m.id)
                except:
                    pass
                continue

            handle(m.text, thread.id, sender, sender_id, reply_user, reply_user_id)

        time.sleep(3)

    except Exception as e:
        print(f"❌ خطأ في اللوب الرئيسي: {e}")
        time.sleep(10)
