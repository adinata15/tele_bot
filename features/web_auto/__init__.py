import logging

from telegram import Update, BotCommand, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from utils import(
    WEB, MENU, END,
)

# Web states
GET_EXEC = range(5,6)

# tbd
def placeholder_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.warning(f'Just a placeholder function ...')
    return END

web_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(placeholder_func, pattern="^" + str(WEB) + "$")],
    states={
        GET_EXEC: [
            MessageHandler(
                filters.TEXT & filters.Regex("^" + str(END) + "$"), 
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