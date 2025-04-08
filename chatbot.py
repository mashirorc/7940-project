import threading
from telegram import Update
from ChatGPT_HKBU import HKBU_ChatGPT
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
import mysql.connector
from dotenv import load_dotenv
import os
import logging
import socketserver
from http.server import BaseHTTPRequestHandler

global connection
def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    load_dotenv('secrets.env')
    updater = Updater(token=os.environ['TELEGRAM_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # setup response to warmup request
    httpd = socketserver.TCPServer(("", 80), MyHandler)
    threading.Thread(target=httpd.serve_forever).start()
    
    connect_to_db()
    # create_table()
    # add_user("tom", "rocket league")
    # add_user("charlie", "league of legends")
    # add_user("alan", "halo")
    clear_table()
    # fetch_users()
    #
    # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equipped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))

    # To start the bot:
    updater.start_polling()
    updater.idle()
def equipped_chatgpt(update, context):
    global chatgpt
    engineered_message = f"""
        Extract the following information from the given text, if there is any. Use the official names for games:
        - The game user wants to play.
        Reply in the format: "game: game name"
        For example: "Find me a Rocket League team for tonight."
        Output: "game: Rocket League"
        Text to analyze: "{update.message.text}"
        If there is no game mentioned in the text, ask the user to ask for a specific game.
    """
    reply_message = chatgpt.submit(engineered_message)
    if "game: " in reply_message:
        logging.info("game request detected")
        game_name = reply_message.split(":")[1].strip().replace('"', '')
        logging.info(f"game name: {game_name}")
        name = update.message.from_user.first_name
        user = find_user_by_name(name)
        interested_user = find_user_by_interest(game_name)
        if user:
            logging.info(f"user found: {user}")
            reply_message = f"Hi {name}, {interested_user} is interested in playing {game_name}."
        else:
            add_user(update.message.from_user.first_name, game_name)
            reply_message = f"Hi {name}, looks like currently no one is interested in playing {game_name}."
    else:
        reply_message = chatgpt.submit("Write a message asking the user for a specific game they want to play in normal conversation style.")
    
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    logging.info(context.args[0])
    update.message.reply_text(""" 
                              /hello <name> - To say hello to someone.
                              /help - To display this message.
                              """)
def hello(update: Update, context: CallbackContext) -> None:
    try:
        logging.info(context.args[0])
        name = context.args[0] # /add keyword <-- this should store the keyword
        update.message.reply_text(f'Good day, {name}!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <name>')
def connect_to_db():
    try:
        global connection
        connection = mysql.connector.connect(
            host=os.environ['SQL_HOST'],
            user=os.environ['SQL_USERNAME'],
            password=os.environ['SQL_PWD'],
            database=os.environ['SQL_DBNAME']
        )
        # integrate mysql logging to python logging
        logger = logging.getLogger("mysql.connector")
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler())
        if connection.is_connected():
            logging.info("connect to db successfully")
            return connection
    except mysql.connector.Error as error:
        logging.error("Failed to connect to database: {}".format(error))

def create_table():
    try:
        global connection
        cursor = connection.cursor()
        sql = """CREATE TABLE IF NOT EXISTS USERS
        (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            interest VARCHAR(255) NOT NULL
        );"""
        cursor.execute(sql)
        connection.commit()
        logging.info("Table created successfully")
    except mysql.connector.Error as error:
        logging.error("Failed to create table: {}".format(error))

def fetch_users():
    try:
        global connection
        cursor = connection.cursor()
        sql = "SELECT * FROM USERS"
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            logging.info(row)
    except mysql.connector.Error as error:
        logging.error("Failed to fetch data: {}".format(error))

def add_user(name, interest):
    try:
        global connection
        cursor = connection.cursor()
        sql = "INSERT INTO USERS (name, interest) VALUES (%s, %s)"
        val = (name, interest)
        cursor.execute(sql, val)
        connection.commit()
        logging.info("User added successfully")
    except mysql.connector.Error as error:
        logging.error("Failed to insert data: {}".format(error))

def find_user_by_name(name):
    try:
        global connection
        cursor = connection.cursor()
        sql = "SELECT * FROM USERS WHERE name LIKE %s"
        val = ("%" + name + "%",)
        cursor.execute(sql, val)
        results = cursor.fetchall()
        if results:
            logging.info("User with specified name found")
            return results[0]
        else:
            logging.info("User with specified name not found")
            return None
    except mysql.connector.Error as error:
        logging.error("Failed to fetch data: {}".format(error))

def find_user_by_interest(interest):
    try:
        global connection
        cursor = connection.cursor()
        sql = "SELECT * FROM USERS WHERE interest LIKE %s"
        val = ("%" + interest + "%",)
        cursor.execute(sql, val)
        results = cursor.fetchall()
        if results:
            logging.info("User with specified interest found")
            return results[0][1]
        else:
            logging.info("User with specified interest not found")
            return None
    except mysql.connector.Error as error:
        logging.error("Failed to fetch data: {}".format(error))
    
def clear_table():
    try:
        global connection
        cursor = connection.cursor()
        sql = "DELETE FROM USERS"
        cursor.execute(sql)
        connection.commit()
        logging.info("Table cleared successfully")
    except mysql.connector.Error as error:
        logging.error("Failed to clear table: {}".format(error))

def warmup():
    logging.info("Respond to warmup request")

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            warmup()

        self.send_response(200)



if __name__ == '__main__':
    main()