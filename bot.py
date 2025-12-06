import telebot
from flask import Flask, request
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- TELEGRAM BOT ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Set this on Render or GitHub Secrets
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g., https://your-bot.onrender.com

# --- FIREBASE SETUP FROM ENV ---
firebase_key_json = os.environ.get("FIREBASE_KEY")  # Entire JSON as a string
cred_dict = json.loads(firebase_key_json)

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection("users")

# --- FIRESTORE FUNCTIONS ---
def user_exists(user_id):
    return users_ref.document(str(user_id)).get().exists

def add_user(user_id):
    users_ref.document(str(user_id)).set({"id": user_id})

def get_total_users():
    return len(list(users_ref.stream()))

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        add_user(user_id)

    total_users = get_total_users()

    bot.send_message(
        message.chat.id,
        "👋 እንኳን ወደ ለውጥ ፕላስ ቦት በደህና መጡ!\n"
        "ይህ ቦት የጤና እና የእንቅስቃሴ ሕይወት ለማሻሻል የተሰራ ነው።\n\n"
        "👋 Welcome to Lewt Plus Bot!\n"
        f"👥 Total users: {total_users}"
    )

    img_path = os.path.join(os.path.dirname(__file__), "tena.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as img:
            bot.send_photo(message.chat.id, img)

# Admin stats
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"👥 Total users: {get_total_users()}")
    else:
        bot.send_message(message.chat.id, "🚫 You are not authorized.")

# --- WEBHOOK ROUTE ---
@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "", 200

# --- SET WEBHOOK ---
bot.remove_webhook()
bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
