import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
import yfinance as yahooFinance
# import pandas as pd
import logging

logging.basicConfig(format='[%(asctime)s][%(funcName)s(%(lineno)d)][%(levelname)s]:%(message)s', level=logging.INFO, filename="logs/info.log")

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8088))
HEROKU_URL = os.environ.get('HEROKU_URL')

# Updater data
# {
#     "update_id":507888169,
#     "message":{
#         "message_id":250,
#         "date":1702815105,
#         "chat":{
#             "id":828279473,
#             "type":"private",
#             "username":"decococrunch",
#             "first_name":"Adi Nata"
#         },
#         "text":"/start",
#         "entities":[
#             {
#                 "type":"bot_command",
#                 "offset":0,
#                 "length":6
#             }
#         ],
#         "caption_entities":[
            
#         ],
#         "photo":[
            
#         ],
#         "new_chat_members":[
            
#         ],
#         "new_chat_photo":[
            
#         ],
#         "delete_chat_photo":false,
#         "group_chat_created":false,
#         "supergroup_chat_created":false,
#         "channel_chat_created":false,
#         "from":{
#             "id":828279473,
#             "first_name":"Adi Nata",
#             "is_bot":false,
#             "username":"decococrunch",
#             "language_code":"en"
#         }
#     }
# }


# bot = telebot.TeleBot(BOT_TOKEN)

# @bot.message_handler(commands=['history'])
# def send_company_history_data(message):
#     # Show summary of data instead?

#     logging.info(f"Entered function")
#     if(message.content_type != 'text'):
#         bot.reply_to(message, "Please input the code of the shares in text format")
#         return
    
#     tokens = message.text.split()
#     if(len(tokens) == 2):
#         logging.info(f"Valid tokens amount")
#         company_ticker = get_company_ticker_from_stock_code(tokens[1])
#         historical_data = get_company_historical_data(company_ticker)
#         printable = print_object(historical_data, ignored_keys=["companyOfficers", "longBusinessSummary"])
#         tele_safe_send(message, printable)

# @bot.message_handler(commands=['info'])
# def send_company_info(message):
#     logging.info(f"Entered function")
#     if(message.content_type != 'text'):
#         bot.reply_to(message, "Please input the code of the shares in text format")
#         return
    
#     tokens = message.text.split()
#     if(len(tokens) == 2):
#         logging.info(f"Valid tokens amount")
#         company_ticker = get_company_ticker_from_stock_code(tokens[1])
#         printable = print_object(company_ticker.info, ignored_keys=["companyOfficers", "longBusinessSummary"])
#         tele_safe_send(message, printable)

# @bot.message_handler(commands=['help'])
# def send_help(message):
#     logging.info(f"Entered function")
#     bot.reply_to(message, "Here are some of the function we support for now:\
#                  \n /hello : this will start bot execution \n")

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Entered function")
    print(f"Update: {update}")
    # print_object(update)
    print(f"Context: {context}")
    # print_object(context)

    user = update.message.from_user
    # msg = update.message.text
    # await == async wait (we are telling the program -> while waiting for this you can do other stuff first)
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "Hi, how can I help you?")

# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)

# def tele_safe_send(message, data: str):
#     logging.info(f"Entered function")

#     if len(data) >= 4096:
#         for x in range(0, len(data), 4096):
#             bot.reply_to(message, data[x:x+4096])
#     else:
#         bot.reply_to(message, data)

# def get_company_historical_data(stock_ticker: yahooFinance.Ticker) -> pd.DataFrame:
#     return stock_ticker.history(period="1d", interval="1m")

# def get_company_ticker_from_stock_code(stock_code:str) -> yahooFinance.Ticker:
#     return yahooFinance.Ticker(stock_code)

def print_object(generic_object: object, ignored_keys: list = None) -> str:
    logging.info(f"Entered function")
    logging.debug(f"Generic Object: {generic_object}")

    printable = str()
    for key, value in generic_object.items():
        if(key not in ignored_keys):
            printable += f"{key} : {value}\n"
    return printable

# def parse_json(stock_ticker: yahooFinance.Ticker):
#     for key, value in stock_ticker.info.items():
#         print(key, ":", value)

def log_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.warning(f'Update {update} caused error {context.error}')

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        logging.error("Wrong input format for application")
        print("Usage: python bot.py <devel/deploy>")

    logging.debug(f"Running on {sys.argv[1]} mode")
    # TBD :register/login account

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', send_welcome)
    application.add_handler(start_handler)
    
    application.add_error_handler(log_error)

    arguments = sys.argv
    if(sys.argv[1] == 'devel'):
        application.run_polling()
    elif(sys.argv[1] == 'deploy'):
        # to be reviewed
        application.run_webhook(
            listen='0.0.0.0',
            port=PORT,
            webhook_url=HEROKU_URL
        )

        # updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=BOT_TOKEN)
        # updater.bot.setWebhook(HEROKU_URL + BOT_TOKEN)
        

