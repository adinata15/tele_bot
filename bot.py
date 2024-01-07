import os
import sys
from telegram import Update, BotCommand, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging

from features.stocks import (
    stock_handler,
)

from features.web_auto import (
    web_handler,
)

from utils import (
    END, STOCKS, WEB, MENU,
)

logging.basicConfig(format='[%(asctime)s][%(funcName)s(%(lineno)d)][%(levelname)s]:%(message)s', level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logger = logging.getLogger("httpx").setLevel(logging.DEBUG)

# Credentials setup
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8088))
HEROKU_URL = os.environ.get('HEROKU_URL')

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

    start_handler = CommandHandler('start', start)
    end_handler = CommandHandler('end', send_goodbye)

    main_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            MENU: [
                stock_handler,
                web_handler,
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
