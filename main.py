from telebot import types
import telebot
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")

genai.configure(api_key=API_KEY)
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "user.json"
DRUGS_FILE = "drugs.json"

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

def load_drugs():
    with open(DRUGS_FILE, 'r') as f:
        return json.load(f)


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


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Register", "Log In")
        bot.send_message(
            message.chat.id,
            "Hi! This bot lets you describe your symptoms to AI for possible solutions, "
            "and explore information about illnesses and drugs."
        )
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "register")
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

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "log in")
def login(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
        bot.send_message(message.chat.id, "You have already logged in!")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "You are not registered yet. Please register first!")

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "log out")
def logout(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        del users[user_id]
        save_users()
        print(f"{user_id} logged out.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Register", "Log In")
    bot.send_message(message.chat.id, "You've been logged out.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "about this bot")
def about_bot(message):
    markup_about = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup_about.add(types.KeyboardButton("Back to Menu"))
    bot.send_message(
        message.chat.id,
        "This bot lets you:\n"
        "- Describe your symptoms to AI and get possible solutions.\n"
        "- Explore illnesses and treatments.\n"
        "- Search for drug information.",
        reply_markup=markup_about
    )


@bot.message_handler(func=lambda message: message.text.lower() == "drugs")
def drugs_info(message):
    user_id = str(message.from_user.id)
    user_mode[user_id] = "drugs"

    markup_drug = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup_drug.add(types.KeyboardButton("Back to Menu"))

    bot.send_message(
        message.chat.id,
        "Drug Search Mode Activated.\nEnter the drug name (exact or partial).\nPress 'Back to Menu' to exit.",
        reply_markup=markup_drug
    )


@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "symptom checker")
def symptom_checker(message):
    user_id = str(message.from_user.id)
    user_mode[user_id] = "symptom_checker"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Back to Menu"))
    bot.send_message(
        message.chat.id,
        "Symptom Checker Mode Activated.\nDescribe your symptoms.\nPress 'Back to Menu' to exit.",
        reply_markup=markup
    )


data_illness = {
    "infectious": "Infectious illnesses spread from person to person via germs.",
    "deficiency": "Caused by lack of essential nutrients.",
    "hereditary": "Passed from parents to children via genes.",
    "environmental": "Caused by harmful environmental factors.",
    "chronic": "Long-lasting illnesses.",
    "acute": "Sudden and short-term illnesses."
}

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "types of illnesses")
def types_illness(message):
    markup_type = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup_type.add(*data_illness.keys(), "Back to Menu")
    bot.send_message(message.chat.id, "Choose a type of illness:", reply_markup=markup_type)

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() in data_illness)
def info_type_ill(message):
    key = message.text.strip().lower()
    bot.send_message(message.chat.id, f"{key.capitalize()} Illness Info: {data_illness[key]}")


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = str(message.from_user.id)


    if not is_authenticated(user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Register", "Log In")
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot.", reply_markup=markup)
        return

    text = message.text.strip().lower()


    if text == "back to menu":
        main_menu(message)
        return

    mode = user_mode.get(user_id, "menu")


    if mode == "drugs":
        drugs = load_drugs()
        found = False
        for drug in drugs:
            if drug["name"].lower() == text:
                bot.send_message(
                    message.chat.id,
                    f"Name: {drug['name']}\n"
                    f"Description: {drug.get('description', 'N/A')}\n"
                    f"Dosage: {drug.get('dosage', 'N/A')}\n"
                    f"Type: {drug.get('type', 'N/A')}"
                )
                found = True
                break
        if not found:
            bot.send_message(message.chat.id, f"No drug like '{text}' found.")
        return


    if mode == "symptom_checker" and text != "back to menu":
        bot.send_message(message.chat.id, "Analyzing your symptoms... Please wait.")
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(message.text.strip())
            bot.send_message(message.chat.id, response.text)
        except Exception as e:
            bot.send_message(message.chat.id, f"AI error: {str(e)}")
        return


    if mode == "menu":
        bot.send_message(message.chat.id, "Please choose an option from the menu.")
        main_menu()
        
# ---------------- Run Bot ----------------
if __name__ == "__main__":
    print("Bot running....")
    bot.remove_webhook()
    print("Webhook removed!")
    bot.infinity_polling()
