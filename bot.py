import telebot
from flask import Flask, request

TOKEN = '8273421966:AAFRsOqLXr89uogAntyHmiRaj82xcz4icGY'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_URL = 'https://lewtplus-bot.onrender.com'  # your Render URL

# Bot commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 እንኳን ወደ ሉውት ፕላስ ቦት በደህና መጡ\n"
        "ይህ ቦት እንቅስቃሴን ለመቀየር እና እርስዎን ለማጠናከር የተዘጋጀ ነው።\n"
        "👋 Welcome to Lewt Plus Bot \n"
        "A Fitness bot intended to help you change"
    )
    bot.send_photo(message.chat.id, "https://raw.githubusercontent.com/lewtplus/lewtplus-bot/main/tena.jpg")

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
