from telegram import Update
from ChatGPT_HKBU import HKBU_ChatGPT
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
# import configparser
import os
import logging
import redis
global redis1
def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['TELEGRAM_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(os.environ['REDIS_HOST']),
                         password=(os.environ['REDIS_PWD']),
                         port=(os.environ['REDIS_PORT']),
                         decode_responses=(os.environ['REDIS_DECODE']),
                         username=(os.environ['REDIS_USERNAME']))
    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equipped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))

    # To start the bot:
    updater.start_polling()
    updater.idle()
def equipped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
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
    update.message.reply_text("""/add <keyword> - To add a keyword to the database, echos the keyword and the numebr of times it has been said back.
                              /hello <name> - To say hello to someone.
                              /help - To display this message.
                              """)
def add(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
def hello(update: Update, context: CallbackContext) -> None:
    try:
        logging.info(context.args[0])
        name = context.args[0] # /add keyword <-- this should store the keyword
        update.message.reply_text(f'Good day, {name}!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <name>')
if __name__ == '__main__':
    main()