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
ADMIN_ID = int(os.environ.get("ADMIN_ID") or 0)

if not TOKEN:
    raise Exception("TELEGRAM_TOKEN is missing")
if not FIREBASE_KEY:
    raise Exception("FIREBASE_KEY is missing")

# --------------------------
# 2. FIREBASE INIT
# --------------------------
cred_dict = json.loads(FIREBASE_KEY)
cred = credentials.Certificate(cred_dict)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection("users")

# --------------------------
# 3. FLASK + BOT INIT
# --------------------------
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)   # Fixed: was 'name'

# --------------------------
# 4. FIRESTORE FUNCTIONS
# --------------------------
def user_exists(user_id):
    return users_ref.document(str(user_id)).get().exists

def add_user(user_id):
    users_ref.document(str(user_id)).set({
        "id": user_id
    })

def get_total_users():
    return len(list(users_ref.stream()))

# --------------------------
# 5. COMMANDS
# --------------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        add_user(user_id)
    
    total_users = get_total_users()

    welcome_text = (
        "👋 *Welcome to Lewt Plus Premium Bot!*\n"
        "Your fitness companion for a strong and healthy lifestyle.\n\n"
        "💪 እንኳን ወደ ለውጥ ፕላስ ፕሪሚየም ቦት በደህና መጡ\n\n"
        f"👥 *Total Users:* {total_users}\n\n"
        "🔓 *Premium Access Required*\n"
        "📞 +251991226530\n"
        "💬 https://wa.me/251991226530\n"
        "📩 https://t.me/Bruk_Bedlu"
    )

    # === ADD BUTTON HERE ===
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("ℹ️ About Lewt Plus", callback_data="about_lewt"))

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

    # Send photo
    img_path = os.path.join(os.path.dirname(__file__), "tena.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as img:
            bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"👥 Total users: {get_total_users()}")
    else:
        bot.send_message(message.chat.id, "🚫 Not authorized.")


# ======================
# NEW: BUTTON CALLBACK HANDLER
# ======================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "about_lewt":
        about_text = (
            "🏋️‍♂️ *Lewt Plus Premium*\n\n"
            "Your ultimate fitness companion in Ethiopia 🇪🇹\n\n"
            "✅ Personalized workout plans\n"
            "✅ Nutrition guidance\n"
            "✅ Progress tracking\n"
            "✅ Expert support\n\n"
            "🔥 Ready to transform your body?\n"
            "Contact us for Premium Access!"
        )
        
        bot.answer_callback_query(call.id, "✓ Opening info...")
        bot.send_message(call.message.chat.id, about_text, parse_mode="Markdown")


# --------------------------
# 6. WEBHOOK ROUTES
# --------------------------
@app.route('/', methods=['GET'])
def home():
    return "Bot is running", 200

@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200


# --------------------------
# 7. START WEBHOOK
# --------------------------
bot.remove_webhook()
if WEBHOOK_URL:
    bot.set_webhook(url=WEBHOOK_URL)

# --------------------------
# 8. RUN APP
# --------------------------
if __name__ == "__main__":   # Fixed
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
