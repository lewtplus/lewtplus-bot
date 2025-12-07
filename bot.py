import os
import json
from flask import Flask, request
import telebot
import firebase_admin
from firebase_admin import credentials, firestore

# --------------------------
# 1. READ ENVIRONMENT VARIABLES
# --------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
FIREBASE_KEY = os.environ.get("FIREBASE_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))  # Your Telegram user ID

# --------------------------
# 2. INITIALIZE FIREBASE
# --------------------------
cred_dict = json.loads(FIREBASE_KEY)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection("users")

# --------------------------
# 3. INITIALIZE TELEGRAM BOT
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

    # Beautiful welcome text
    welcome_text = (
        "👋 **Welcome to Lewt Plus Bot!**\n"
        "Your fitness companion for a strong and healthy lifestyle.\n\n"
        "💪  እንኳን ወደ ለውጥ ፕላስ ቦት በደህና መጡ\n" 
        "ይህ ቦት እንቅስቃሴን ለመቀየር እና እርስዎን ለማጠናከር የተዘጋጀ ነው።\n\n"
        f"👥 **Total Users:** {total_users}\n"
        "🚀 Let’s start your fitness journey!"
    )

    # Send image + text together
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
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")


# Admin-only stats
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            f"👥 Total registered users: {get_total_users()}"
        )
    else:
        bot.send_message(message.chat.id, "🚫 You are not authorized.")


# --------------------------
# 6. WEBHOOK ROUTE
# --------------------------
@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "", 200

# --------------------------
# 7. SET WEBHOOK AND RUN
# --------------------------
bot.remove_webhook()
bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
