import os
import json
import time
from flask import Flask, request
import telebot
import firebase_admin
from firebase_admin import credentials, firestore

# --------------------------
# 1. ENV VARIABLES
# --------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
FIREBASE_KEY = os.environ.get("FIREBASE_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID") or 0)

if not TOKEN or not WEBHOOK_URL:
    raise Exception("Missing TELEGRAM_TOKEN or WEBHOOK_URL")

if not FIREBASE_KEY:
    raise Exception("FIREBASE_KEY is missing!")

# --------------------------
# 2. FIREBASE INIT
# --------------------------
cred_dict = json.loads(FIREBASE_KEY)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection("users")

# --------------------------
# 3. BOT + FLASK APP
# --------------------------
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --------------------------
# 4. FIRESTORE FUNCTIONS
# --------------------------
def user_exists(user_id):
    return users_ref.document(str(user_id)).get().exists

def add_user(user_id):
    users_ref.document(str(user_id)).set({"id": user_id})

def get_total_users():
    return len(list(users_ref.stream()))

# --------------------------
# 5. TELEGRAM COMMANDS
# --------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    if not user_exists(user_id):
        add_user(user_id)

    total_users = get_total_users()

    welcome_text = (
        "👋 *Welcome to Lewt Plus Premium Bot!*\n"
        "Your fitness companion for a strong and healthy lifestyle.\n\n"

        "💪 እንኳን ወደ ለውጥ ፕላስ ፕሪሚየም ቦት በደህና መጡ\n"
        "ይህ ቦት ሙሉ አገልግሎት ለማግኘት የተዘጋጀ ነው።\n\n"

        f"👥 *Total Users:* {total_users}\n\n"

        "🔓 *Premium Access Required*\n"
        "Contact us:\n\n"
        "📞 +251991226530\n"
        "💬 https://wa.me/251991226530\n"
        "📩 https://t.me/Bruk_Bedlu\n\n"

        "🚀 *Join the Change!*"
    )

    img_path = os.path.join(os.path.dirname(__file__), "tena.jpg")

    if os.path.exists(img_path):
        with open(img_path, "rb") as img:
            bot.send_photo(
                message.chat.id,
                img,
                caption=welcome_text,
                parse_mode="Markdown"
            )
    else:
        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode="Markdown"
        )

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            f"👥 Total users: {get_total_users()}"
        )
    else:
        bot.send_message(message.chat.id, "🚫 Not authorized.")

# --------------------------
# 6. WEBHOOK ROUTE
# --------------------------
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(
        request.data.decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

# Health check (important)
@app.route("/", methods=["GET"])
def home():
    return "Bot is running 🚀"

# --------------------------
# 7. START SERVER
# --------------------------
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
