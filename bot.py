import telebot

# Replace with your token
TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# When user presses Start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 እንኳን ወደ ሉውት ፕላስ ቦት በደህና መጡ\n"
        "ይህ ቦት እንቅስቃሴን ለመቀየር እና እርስዎን ለማጠናከር የተዘጋጀ ነው።\n"
        "👋 Welcome to Lewt Plus Bot \n"
        "A Fitness bot intended to help you change"
    )

    # ✅ Send an image from a public URL
    bot.send_photo(
        message.chat.id,
        "https://raw.githubusercontent.com/lewtplus/lewtplus-bot/main/tena.jpg",  # Example: GitHub raw link
        caption="💪 Lewt Plus Bot Logo"
    )

bot.polling()