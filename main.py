import json
import os
from telebot import types
import telebot

TOKEN = "7332690649:AAHO61UwFAYQqFvINOsLIq_ixlSSgulE17M"
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"

illness_data = {
    "infectious": {"illness_name": "Info"},
    "deficiency": {"illness_name": "Info"},
    "hereditary": {"illness_name": "Info"},
    "environmental": {"illness_name": "Info"},
    "chronic": {"illness_name": "Info"},
    "acute": {"illness_name": "Info"}
}


if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def is_authenticated(user_id):
    return str(user_id) in users


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Register", "Log In")
        bot.send_message(message.chat.id, "Welcome! Please Register or Log In to use the bot.", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text.lower() == "register")
def register(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        bot.send_message(message.chat.id, "You're already registered.")
        main_menu(message)
        return
    msg = bot.send_message(message.chat.id, "Enter your name:")
    bot.register_next_step_handler(msg, process_register_name)

def process_register_name(message):
    name = message.text.strip()
    user_id = str(message.from_user.id)
    users[user_id] = {"name": name}
    save_users()
    bot.send_message(message.chat.id, f"Thanks {name}, you are now registered!")
    main_menu(message)


@bot.message_handler(func=lambda m: m.text.lower() == "log in")
def login(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        bot.send_message(message.chat.id, "You're already logged in.")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "You're not registered yet. Please register first.")


def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("About this bot", "AI Chat", "Illnesses", "Drugs", "Log Out")
    bot.send_message(message.chat.id, "Main Menu:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.lower() == "about this bot")
def about_bot(message):
    bot.send_message(message.chat.id,
        "This bot allows you to describe your symptoms to AI and get helpful suggestions. "
        "It also provides info about different illnesses and treatments.")


@bot.message_handler(func=lambda m: m.text.lower() == "illnesses")
def illness_types(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*illness_data.keys(), "Back to Menu")
    bot.send_message(message.chat.id, "Choose a type of illness:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.lower() in illness_data)
def illness_info(message):
    key = message.text.lower()
    bot.send_message(message.chat.id, f"{key.capitalize()} illness: {illness_data[key]['illness_name']}")



@bot.message_handler(func=lambda m: m.text.lower() == "drugs")
def drugs(message):
    bot.send_message(message.chat.id, "Drugs information coming soon...")

@bot.message_handler(func=lambda m: m.text.lower() == "ai chat")
def ai_chat(message):
    bot.send_message(message.chat.id, "AI chat coming soon...")

@bot.message_handler(func=lambda m: m.text.lower() == "back to menu")
def back_to_menu(message):
    main_menu(message)


@bot.message_handler(func=lambda m: m.text.lower() == "log out")
def logout(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        del users[user_id]
        save_users()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Register", "Log In")
    bot.send_message(message.chat.id, "You've been logged out.", reply_markup=markup)


@bot.message_handler(func=lambda m: True)
def block_unauthorized(message):
    if not is_authenticated(str(message.from_user.id)):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Register", "Log In")
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot.", reply_markup=markup)

bot.remove_webhook()
print("Webhook removed.")
bot.infinity_polling()
