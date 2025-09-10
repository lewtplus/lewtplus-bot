import telebot

# Replace with your token
TOKEN = '8273421966:AAFRsOqLXr89uogAntyHmiRaj82xcz4icGY'
bot = telebot.TeleBot(TOKEN)

# When user presses Start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 እንኳን  ወደ ሉውት ፕላስ ቦት በደህና መጡ\nይህ ቦት እንቅስቃሴን ለመቀየር እና እርስዎን ለማጠናከር የተዘጋጀ ነው።\n👋 Welcome to Lewt Plus Bot \n A Fitness bot intended to help you change")

    # Send an image (replace with your own URL or file path)
    with open(r"C:\Users\Bruk\Desktop\Lewt Logo\tena.jpg", "rb") as photo:
        bot.send_photo(message.chat.id, photo)   # ✅ properly indented

bot.polling()
