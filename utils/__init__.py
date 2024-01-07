import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

# General states
STOCKS, WEB, MENU, END_PROGRAM = range(4)
# end only to exit current execution (like "back" button)
END = ConversationHandler.END

async def tele_safe_send(context: ContextTypes, update: Update, data: str):
    logging.info(f"Entered function")

    if len(data) >= 4096:
        for x in range(0, len(data), 4096):
            await context.bot.send_message(chat_id = update.effective_chat.id, text = data[x:x+4096])
    else:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = data)

def print_object(generic_object: object, ignored_keys: list = None) -> str:
    logging.info(f"Entered function")
    logging.debug(f"Generic Object: {generic_object}")

    printable = str()
    for key, value in generic_object.items():
        if(key not in ignored_keys):
            printable += f"{key} : {value}\n"
    return printable