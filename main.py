import os
import json
import time
import telebot
from flask import Flask, request
from telebot import types
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
API_KEY = os.getenv("AI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN is not set in environment variables!")
if not API_KEY:
    raise ValueError("⚠️ AI_API_KEY is not set in environment variables!")

# Configure Gemini AI
genai.configure(api_key=API_KEY)

# Init Flask + bot
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# Files for user + drugs
USERS_FILE = "user.json"
DRUGS_FILE = "drugs.json"

# Load users
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

user_mode = {}

# --- Helpers ---
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_authenticated(user_id):
    return str(user_id) in users

def load_drugs():
    if os.path.exists(DRUGS_FILE):
        with open(DRUGS_FILE, "r") as f:
            return json.load(f)
    return []

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

# --- Bot Handlers ---

@bot.message_handler(commands=["start"])
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
            "and explore information about illnesses and drugs.",
            reply_markup=markup
        )

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

data_illness = {
    "infectious": "Infectious illnesses spread from person to person via germs.",
    "deficiency": "Caused by lack of essential nutrients.",
    "hereditary": "Passed from parents to children via genes.",
    "environmental": "Caused by harmful environmental factors.",
    "chronic": "Long-lasting illnesses.",
    "acute": "Sudden and short-term illnesses."
}

popular_ilnesses = {
    "Influenza (Flu)": "A contagious respiratory illness caused by influenza viruses, leading to fever, cough, sore throat, and body aches.",
    "Common Cold": "A mild viral infection of the nose and throat, causing sneezing, runny nose, and sore throat.",
    "COVID-19": "A respiratory illness caused by the SARS-CoV-2 virus, with symptoms ranging from mild cough to severe pneumonia.",
    "Diabetes": "A chronic condition where the body either doesn't produce enough insulin or can't effectively use it, leading to high blood sugar.",
    "Hypertension (High Blood Pressure)": "A condition where the force of blood against artery walls is consistently too high, increasing heart disease risk.",
    "Asthma": "A chronic respiratory condition causing airway inflammation, difficulty breathing, wheezing, and coughing.",
    "Tuberculosis (TB)": "A bacterial infection mainly affecting the lungs, spread through airborne particles from an infected person.",
    "Malaria": "A mosquito-borne disease caused by Plasmodium parasites, leading to fever, chills, and flu-like symptoms.",
    "HIV/AIDS": "A viral infection that attacks the immune system, weakening the body's defense against infections and certain cancers.",
    "Cancer": "A group of diseases involving abnormal cell growth that can invade or spread to other parts of the body."
}

@bot.message_handler(func=lambda message: message.text.strip().lower() == "popular illnesses")
def popular_ill(message):
    markup_popular = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup_popular.add(*popular_ilnesses.keys(), "Back to Menu")
    bot.send_message(message.chat.id, "Here are 10 popular illnesses. Choose a popular illness to get information", reply_markup=markup_popular)

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() in [ill.lower() for ill in popular_ilnesses])
def info_popular_ill(message):
    user_choice = message.text.strip().lower()
    for illness in popular_ilnesses:
        if illness.lower() == user_choice:
            bot.send_message(message.chat.id, f"{illness} Information: {popular_ilnesses[illness]}")
            break

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
        try:
            bot.send_chat_action(message.chat.id, "typing")
            bot.send_message(message.chat.id, "Analyzing your symptoms... Please Wait!")
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(message.text.strip(), stream=True)
            final_text = ""
            for chunk in response:
                if chunk.candidates[0].content.parts:
                    final_text += chunk.candidates[0].content.parts[0].text
                    bot.send_chat_action(message.chat.id, "typing")
                    time.sleep(0.5)
            bot.send_message(message.chat.id, final_text)
        except Exception as e:
            bot.send_message(message.chat.id, f"AI error: {str(e)}")
        return
    if mode == "menu":
        bot.send_message(message.chat.id, "Please choose an option from the menu.")
        main_menu(message)

# --- Webhook Setup ---

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://symphtom-checker.onrender.com{WEBHOOK_PATH}"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running on Render 🚀", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    else:
        return "bad request", 403

# --- Entrypoint ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")
    port = int(os.environ.get("PORT", 10000))
    print(f"🌍 Flask app running on port {port}...")
    app.run(host="0.0.0.0", port=port)
