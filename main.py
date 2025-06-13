from telebot import types  # ✅ Correct import
import telebot

TOKEN = "7332690649:AAHO61UwFAYQqFvINOsLIq_ixlSSgulE17M"
bot = telebot.TeleBot(TOKEN)

# Illnesses mini database
illnesses_db = {
    "headache": "Take a pain reliever like ibuprofen or acetaminophen.",
    "cold": "Rest, stay hydrated, and consider over-the-counter cold medications.",
    "fever": "Stay hydrated and take fever-reducing medication if necessary.",
    "stomach ache": "Try ginger tea or peppermint tea, and avoid heavy foods.",
    "cough": "Honey and warm water can soothe your throat; consider cough syrup if needed."
}

# Start message
@bot.message_handler(commands=['start'])
def start(message):
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Illnesses & Solutions")
    btn2 = types.KeyboardButton("Old and Modern Solutions")
    btn3 = types.KeyboardButton("About Bot")
    btn4 = types.KeyboardButton("Chat with AI")
    start_markup.add(btn1, btn2, btn3, btn4)    
    bot.send_message(message.chat.id, 
        "HI! In this bot you can find solution for illnesses. "
        "Also you can see modern and old solutions for illnesses. "
        "Just write your illness and the bot will find a solution for you.", 
        reply_markup=start_markup)

# Illnesses & Solutions
@bot.message_handler(func=lambda message: message.text.lower() == "illnesses & solutions")
def illnesses_solutions(message):
    response = "Here are the available illnesses and their solutions:\n\n"
    for illness, solution in illnesses_db.items():
        response += f"• {illness.title()}: {solution}\n"
    bot.send_message(message.chat.id, response)

# Old and Modern Solutions
@bot.message_handler(func=lambda message: message.text.lower() == "old and modern solutions")
def old_modern_solutions(message):
    bot.send_message(message.chat.id, "Example:\n• Old: Herbal tea for cough.\n• Modern: Cough syrup.")

# About Bot
@bot.message_handler(func=lambda message: message.text.lower() == "about bot")
def about_bot(message):
    bot.send_message(message.chat.id, 
        "This bot is designed to provide solutions for common illnesses and "
        "compare old and modern remedies. It also features an AI chat function.")

# Chat With AI
@bot.message_handler(func=lambda message: message.text.lower() == "chat with ai")
def chat_with_ai(message):
    bot.send_message(message.chat.id, "This feature is coming soon! Stay tuned.")

bot.infinity_polling()
