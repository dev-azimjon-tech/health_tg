from telebot import types
import telebot

TOKEN = "7332690649:AAHO61UwFAYQqFvINOsLIq_ixlSSgulE17M"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton("About this bot")
    btn2 = types.KeyboardButton("AI Chat")
    btn3 = types.KeyboardButton("Ilnesses")
    btn4 = types.KeyboardButton("Drugs")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(
        message.chat.id, "  ",
        reply_markup=markup
        )
    
@bot.message_handler(func=lambda message:message.text.lower() == "about this bot")
def about_bot(message):
    markup_about = types.ReplyKeyboardMarkup(row_width=1)
    btn = types.KeyboardButton("Back to Menu")
    markup_about.add(btn)
    bot.send_message(
        message.chat.id,
          "This bot allows you to describe your symptoms, and the AI will provide helpful guidance and possible solutions based on your input. Additionally, you can access a library of information about both traditional remedies and modern medical treatments for different illnesses. The goal of this bot is to help you understand your health better, compare solutions, and discover safe, effective methods to feel better.",
          reply_markup=markup_about
        )
@bot.message_handler(func=lambda message:message.text.lower() == "back to menu")
def back_menu(message):
    start_cmd(message)

bot.infinity_polling()
