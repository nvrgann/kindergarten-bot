import telebot
from config import TOKEN, CHAT_ID

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Бот работает!")

# Отправка сообщения при старте
bot.send_message(CHAT_ID, "✅ Бот запущен и работает!")

bot.polling(none_stop=True)