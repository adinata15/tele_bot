import os
import sys
from telegram import Update, BotCommand, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
import yfinance as yahooFinance
import pandas as pd
import logging

logging.basicConfig(format='[%(asctime)s][%(funcName)s(%(lineno)d)][%(levelname)s]:%(message)s', level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logger = logging.getLogger("httpx").setLevel(logging.DEBUG)

# Credentials setup
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8088))
HEROKU_URL = os.environ.get('HEROKU_URL')

# States
# Features
STOCKS, WEB = range(2)
# General states
MENU, END_PROGRAM = range(2, 4)
# Stock states
STOCK_MENU, STOCK_GENERAL_INFO, STOCK_HISTORY, GET_STOCK_CODE, GET_NEXT = range(4, 9)
# Web states
GET_EXEC = range(6)
# end only to exit current execution (like "back" button)
END = ConversationHandler.END

async def get_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['stock_option'] = None
    buttons = [
        [
            InlineKeyboardButton(text="Get stock information", callback_data=str(STOCK_GENERAL_INFO)),
            InlineKeyboardButton(text="Get historical data", callback_data=str(STOCK_HISTORY)),
        ],
        [
            InlineKeyboardButton(text="Back to Menu", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "How can I help on stocks?", reply_markup=keyboard)
    
    return STOCK_MENU

async def get_stock_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(f"Entered function")
    context.user_data["stock_option"] = update.callback_query.data
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "Please enter the stock code of the company. For example: AAPL")
    return GET_STOCK_CODE

async def process_stock_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(f"Entered function")
    stock_code = update.message.text
    stock_option = context.user_data['stock_option']
    company_ticker = get_company_ticker_from_stock_code(stock_code)

    if (stock_option == str(STOCK_GENERAL_INFO)):
        printable = print_object(company_ticker.info, ignored_keys=["companyOfficers", "longBusinessSummary"])
    elif (stock_option == str(STOCK_HISTORY)):
        # in progress
        historical_data = get_company_historical_data(company_ticker)
        logging.info(historical_data)
    else:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = "Options not understood, terminating program")
        return END

    await tele_safe_send(context, update, data=printable)
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "We are done with the stocks, send /start if you have another query :D")
    return END

async def send_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(f"Entered function")
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "Good talking to you, send /start to talk again :D")
    return END

async def get_next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Entered function")
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "Type or choose /start on the menu to do another query")
    return END

async def send_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Entered function")
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "In progress")

async def send_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Entered function")
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "This si all the help i can give. Blame the dev!")

async def tele_safe_send(context: ContextTypes, update: Update, data: str):
    logging.info(f"Entered function")

    if len(data) >= 4096:
        for x in range(0, len(data), 4096):
            await context.bot.send_message(chat_id = update.effective_chat.id, text = data[x:x+4096])
    else:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = data)

def get_company_historical_data(stock_ticker: yahooFinance.Ticker) -> pd.DataFrame:
    return stock_ticker.history(period="1d", interval="1h")

def get_company_ticker_from_stock_code(stock_code:str) -> yahooFinance.Ticker:
    return yahooFinance.Ticker(stock_code)

def print_object(generic_object: object, ignored_keys: list = None) -> str:
    logging.info(f"Entered function")
    logging.debug(f"Generic Object: {generic_object}")

    printable = str()
    for key, value in generic_object.items():
        if(key not in ignored_keys):
            printable += f"{key} : {value}\n"
    return printable

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(f"Entered function")

    buttons = [
        [
            InlineKeyboardButton(text="Stocks", callback_data=str(STOCKS)),
            InlineKeyboardButton(text="Web automate", callback_data=str(WEB)),
        ],
        [
            InlineKeyboardButton(text="End program", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(text = "Hi, what do you wnat to do?", reply_markup=keyboard)
    return MENU

# def parse_json(stock_ticker: yahooFinance.Ticker):
#     for key, value in stock_ticker.info.items():
#         print(key, ":", value)

def log_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.warning(f'Update {update.effective_message} caused error {context.error}')

# tbd
def placeholder_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.warning(f'Just a placeholder function ...')

async def post_init(application: ApplicationBuilder) -> None:
    await application.bot.set_my_commands([
        BotCommand('/start', 'Starts the bot'),
        BotCommand('/settings', 'User settings'),
        BotCommand('/help', 'Get help for commands'),
        BotCommand('/info', 'Get stock info for a particular stock code')
    ])

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        logging.error("Wrong input format for application")
        print("Usage: python bot.py <devel/deploy>")

    logging.debug(f"Running on {sys.argv[1]} mode")
    # TBD :register/login account

    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    stock_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_stock_command, pattern="^" + str(STOCKS) + "$")],
        states={
            STOCK_MENU: [
                CallbackQueryHandler( 
                    get_stock_code,
                    pattern=("^" + str(STOCK_GENERAL_INFO) + "$|^" + str(STOCK_HISTORY) + "$")
                ),
            ],
            GET_STOCK_CODE: [
                MessageHandler(
                    filters.TEXT, 
                    process_stock_request
                )
            ],
        },
        fallbacks=[
            # MessageHandler(filters.Regex("^"+str(END)+"$"), send_goodbye)
        ],
        map_to_parent={
            END: MENU
        }
    )

    start_handler = CommandHandler('start', start)
    end_handler = CommandHandler('end', send_goodbye)
    # tbd
    web_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(placeholder_func, pattern="^" + str(WEB) + "$")],
        states={
            GET_EXEC: [
                MessageHandler(
                    filters.TEXT & filters.Regex("^" + str(GET_STOCK_CODE) + "$"), 
                    placeholder_func
                )
            ],
        },
        fallbacks=[
            # MessageHandler(filters.Regex("^"+str(END)+"$"), send_goodbye)
        ],
        map_to_parent={
            END: MENU
        }
    )

    main_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            MENU: [
                stock_handler,
                web_handler, #tbd
                start_handler,
            ],
            END: [end_handler],
        },
        fallbacks=[
            end_handler,
            CommandHandler('settings', send_settings),
            CommandHandler('help', send_help),
            MessageHandler(filters.Regex("^"+str(END)+"$"), send_goodbye),
        ],
    )

    application.add_handler(main_handler)
  
    application.add_error_handler(log_error)

    arguments = sys.argv
    if(sys.argv[1] == 'devel'):
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    elif(sys.argv[1] == 'deploy'):
        # to be reviewed
        application.run_webhook(
            listen='0.0.0.0',
            port=PORT,
            webhook_url=HEROKU_URL
        )
