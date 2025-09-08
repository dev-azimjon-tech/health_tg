from telebot import types
import telebot
import json
import os
import google.generativeai as genai
import os
from dotenv import load_dotenv
import telebot
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")

genai.configure(api_key=API_KEY)
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()

USERS_FILE = "user.json"

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

user_mode = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_authenticated(user_id):
    return str(user_id) in users

data_illness = {
    "infectious": "",
    "deficiency": "",
    "hereditary": "",
    "environmental": "",
    "chronic": "",
    "acute": ""
}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Register"), types.KeyboardButton("Log In"))
        bot.send_message(
            message.chat.id,
            "Hi! In this bot, you can describe your symptoms to an AI chat and receive possible solutions. "
            "You can also explore both traditional and modern treatments for various illnesses."
        )
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "register")
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
    msg = bot.send_message(message.chat.id, "Now enter your phone number:")
    bot.register_next_step_handler(msg, process_register_phone)

def process_register_phone(message):
    phone = message.text.strip()
    user_id = str(message.from_user.id)
    if user_id in users:
        users[user_id]["phone"] = phone
        save_users()
        bot.send_message(message.chat.id, f"Registration complete!\nName: {users[user_id]['name']}\nPhone: {phone}")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please type 'register' again.")

@bot.message_handler(func=lambda message: message.text and message.text.lower() == "log in")
def login(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        bot.send_message(message.chat.id, "You have already logged in!")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "You are not registered yet. Please register first!")

def main_menu(message):
    user_id = str(message.from_user.id)
    user_mode[user_id] = "menu"
    markup_main = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup_main.add(
        types.KeyboardButton("About This Bot"),
        types.KeyboardButton("Symptom Checker"),
        types.KeyboardButton("Types of Illnesses"),
        types.KeyboardButton("Popular Illnesses"),
        types.KeyboardButton("Drugs"),
        types.KeyboardButton("Log Out")
    )
    bot.send_message(message.chat.id, "Main Menu:", reply_markup=markup_main)

@bot.message_handler(func=lambda message: message.text and message.text.lower() == "about this bot")
def about_bot(message):
    markup_about = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup_about.add(types.KeyboardButton("Back to Menu"))
    bot.send_message(
        message.chat.id,
        "This bot allows you to describe your symptoms, and the AI will provide helpful guidance and possible solutions "
        "based on your input. Additionally, you can access a library of information about both traditional remedies and "
        "modern medical treatments for different illnesses.",
        reply_markup=markup_about
    )

@bot.message_handler(func=lambda message: message.text and message.text.lower() == "back to menu")
def back_menu(message):
    main_menu(message)

@bot.message_handler(func=lambda message: message.text and message.text.lower() == "symptom checker")
def symptom_checker(message):
    user_id = str(message.from_user.id)
    user_mode[user_id] = "symptom_checker"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Back to Menu"))
    bot.send_message(
        message.chat.id,
        "Symptom Checker Mode Activated.\nDescribe your symptoms, and I will provide possible causes and solutions.\nPress 'Back to Menu' anytime to exit.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = str(message.from_user.id)
    mode = user_mode.get(user_id, "menu")
    if mode == "symptom_checker" and message.text.lower() != "back to menu":
        symptoms = message.text.strip()
        bot.send_message(message.chat.id, "Analyzing your symptoms... Please wait.")
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                f"{symptoms}"
            )
            bot.send_message(message.chat.id, response.text)
        except Exception as e:
            bot.send_message(message.chat.id, f"AI error: {str(e)}")
    elif message.text.lower() == "back to menu":
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


def ads(message):
    bot.send_message(message.chat.id, "Comming soon")

bot.remove_webhook()
bot.infinity_polling()