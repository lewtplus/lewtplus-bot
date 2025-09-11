import telebot
from flask import Flask, request
import os

TOKEN = '8273421966:AAFRsOqLXr89uogAntyHmiRaj82xcz4icGY'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_URL = 'https://lewtplus-bot.onrender.com'  # your Render URL

# Bot commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 እንኳን ወደ ለውጥ ፕላስ ቦት በደህና መጡ\n"
        "ይህ ቦት እንቅስቃሴን ለመቀየር እና እርስዎን ለማጠናከር የተዘጋጀ ነው።\n"
        "👋 Welcome to Lewt Plus Bot \n"
        "A Fitness bot intended to help you change"
    )

    # Get the absolute path to the image in the project folder
    image_path = os.path.join(os.path.dirname(__file__), "tena.jpg")

    with open(image_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)

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
