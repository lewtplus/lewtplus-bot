import os
import json
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
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

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
# 3. BOT + APP
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

    # Add user if new
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
        "To get full access, contact us:\n\n"

        "📞 Phone: +251991226530\n"
        "💬 WhatsApp: https://wa.me/251991226530\n"
        "📩 Telegram: https://t.me/Bruk_Bedlu\n\n"

        "🚀 *Join the Change!*"
    )

    # Send image + text
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

# --------------------------
# ADMIN COMMAND
# --------------------------
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            f"👥 Total registered users: {get_total_users()}"
        )
    else:
        bot.send_message(
            message.chat.id,
            "🚫 You are not authorized."
        )

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

# Health check (IMPORTANT)
@app.route("/", methods=["GET"])
def home():
    return "Bot is running 🚀"

# --------------------------
# 7. START APP
# --------------------------
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
