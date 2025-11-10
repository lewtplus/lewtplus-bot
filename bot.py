import telebot
from flask import Flask, request
import os
import json

TOKEN = '8273421966:AAF-E9L4dtMfahza5Mc1rE_6-byZxVM1cno'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_URL = 'https://lewtplus-bot.onrender.com'  # your Render URL

# JSON file to store users
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# Bot commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    # Add new user if not in list
    if user_id not in users:
        users.append(user_id)
        save_users(users)

    total_users = len(users)

    bot.send_message(
        message.chat.id,
        f"👋 እንኳን ወደ ለውጥ ፕላስ ቦት በደህና መጡ!\n"
        f"Welcome to Lewt Plus Bot 💪\n\n"
        f"👥 Total users so far: {total_users}"
    )

    image_path = os.path.join(os.path.dirname(__file__), "tena.jpg")
    with open(image_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)

# Optional: Command to show total users (for admin only)
ADMIN_ID = 123456789  # 👈 replace this with your Telegram user ID

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"👥 Total users: {len(users)}")
    else:
        bot.send_message(message.chat.id, "🚫 You are not authorized to view stats.")

# Webhook route
@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Set webhook
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
