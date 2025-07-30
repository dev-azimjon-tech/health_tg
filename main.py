from telebot import types
import telebot

TOKEN = "7332690649:AAHO61UwFAYQqFvINOsLIq_ixlSSgulE17M"
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
print("Webhook removed.")

# Types of illnesses:

infectious = {"illnes_name":"Info"}


deficiency = {"illnes_name":"Info"}


heriditary = {"illnes_name":"Info"}


evironmental = {"illnes_name":"Info"}

chronic = {"illnes_name":"Info"}

acute = {"illnes_name":"Info"}


@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton("About this bot")
    btn2 = types.KeyboardButton("AI Chat")
    btn3 = types.KeyboardButton("Illnesses")
    btn4 = types.KeyboardButton("Drugs")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(
        message.chat.id, "Hi! In this bot, you can describe your symptoms to an AI chat and receive possible solutions. "
    "You can also explore both traditional and modern treatments for various illnesses.",
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


@bot.message_handler(func=lambda message:message.text.lower() == "illnesses")
def ilness(message):
    markup_illness = types.ReplyKeyboardMarkup(row_width=2)
    type_illness = types.KeyboardButton("Types of Illnesses")
    popular_illnesses = types.KeyboardButton("Popular Illnesses")
    menu_back = types.KeyboardButton("Back to Menu")
    markup_illness.add(type_illness, popular_illnesses, menu_back)
    bot.send_message(message.chat.id, "Choose an option: ", reply_markup=markup_illness)
    



bot.remove_webhook()
bot.infinity_polling()