import yfinance as yahooFinance
import pandas as pd
import logging
from telegram import Update, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from utils import (
    END, STOCKS, MENU,
    tele_safe_send, print_object
)

# Stock states
STOCK_MENU, STOCK_GENERAL_INFO, STOCK_HISTORY, GET_STOCK_CODE, GET_NEXT = range(4, 9)

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

def get_company_historical_data(stock_ticker: yahooFinance.Ticker) -> pd.DataFrame:
    return stock_ticker.history(period="1d", interval="1h")

def get_company_ticker_from_stock_code(stock_code:str) -> yahooFinance.Ticker:
    return yahooFinance.Ticker(stock_code)

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