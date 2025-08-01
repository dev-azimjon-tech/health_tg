from telebot import types
import telebot
import json
import os


TOKEN = "7332690649:AAHO61UwFAYQqFvINOsLIq_ixlSSgulE17M"
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
print("Webhook removed.")

USERS_FILE = "user.json"


if os.path.exists(USERS_FILE):
    with open(USERS_FILE,"r") as f:
        user = json.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_authenticated(user_id):
    return str(user_id) in users


# Types of illnesses:
data_illness = {
    "infectios":"",
    "deficiency":"",
    "heriditary":"",
    "environmental":"",
    "chronic":"",
    "acute":""
}



@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Register")
        btn2 = types.KeyboardButton("Log In")
        markup.add(btn1,btn2)
        bot.send_message(
            message.chat.id,
            "Hi! In this bot, you can describe your symptoms to an AI chat and receive possible solutions. "
        "You can also explore both traditional and modern treatments for various illnesses.",
        )
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot", reply_markup=markup)
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


@bot.message_handler(func=lambda message:message.text.lower() == "log in")
def login(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        bot.send_message(message.chat.id, "You have alredy logged in!")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "You are bot registered yet. Please register first!")

def main_menu(message):
    markup_main = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("About This Bot")
    button2 = types.KeyboardButton("Symptom Checker")
    button3 = types.KeyboardButton("Types of Illnesses")
    button4 = types.KeyboardButton("Popular Illnesses")
    button5 = types.KeyboardButton("Drugs")
    log_out_btn = types.KeyboardButton("Log Out")
    markup_main.add(button1, button2, button3, button4, button5, log_out_btn)
    bot.send_message(message.chat.id, "Main Menu: ", reply_markup=markup_main)


@bot.message_handler(func=lambda message:message.text.lower() == "about this bot")
def about_bot(message):
    markup_about = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn = types.KeyboardButton("Back to Menu")
    markup_about.add(btn)
    bot.send_message(
        message.chat.id,
          "This bot allows you to describe your symptoms, and the AI will provide helpful guidance and possible solutions based on your input. Additionally, you can access a library of information about both traditional remedies and modern medical treatments for different illnesses. The goal of this bot is to help you understand your health better, compare solutions, and discover safe, effective methods to feel better.",
          reply_markup=markup_about
        )
@bot.message_handler(func=lambda message:message.text.lower() == "back to menu")
def back_menu(message):
    main_menu(message)




bot.remove_webhook()
bot.infinity_polling()