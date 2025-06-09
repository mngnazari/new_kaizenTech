from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور نیرو اجرا شد")

USER_HANDLERS = [
    MessageHandler(filters.Regex(r"^کیوبرد نیرو$"), staff_command)
]