import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN, ADMIN, STAFFS
    from utils import create_staff_keyboard
    from handlers.admin_handler import ADMIN_HANDLERS # این شامل add_task_conversation_handler است
    from handlers.user_handler import USER_HANDLERS
except ImportError as e:
    logger.critical(f"Import error: {e}")
    sys.exit(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.debug("Received /start command")
        user = update.effective_user
        if not user:
            logger.warning("No effective user in update")
            return

        user_id = user.id
        logger.info(f"User {user_id} ({user.full_name}) started the bot")

        if user_id == ADMIN["id"]:
            logger.debug("Admin detected")
            staff_inline_keyboard = create_staff_keyboard(STAFFS)
            staff_list = "\n".join([f"- {staff['name']} (آیدی: {staff['id']})" for staff in STAFFS])
            message = (
                f"سلام {ADMIN['name']} عزیز، ادمین گرامی!\n\n"
                "لیست نیروهای شما:\n"
                f"{staff_list}\n\n"
                "لطفا یکی از نیروها را انتخاب کنید:"
            )

            await update.message.reply_text(
                message,
                reply_markup=staff_inline_keyboard
            )
            logger.info("Admin welcome message with inline keyboard sent")

        elif user_id in [staff["id"] for staff in STAFFS]:
            logger.debug("Staff member detected")
            from keyboards import STAFF_KEYBOARD
            await update.message.reply_text(
                "سلام نیروی محترم!",
                reply_markup=STAFF_KEYBOARD
            )
            logger.info("Staff welcome message sent")

        else:
            logger.debug("Regular user detected")
            await update.message.reply_text("سلام کاربر عزیز!")
            logger.info("Regular user welcome message sent")

    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)


def main() -> None:
    try:
        logger.info("Starting bot application...")
        application = Application.builder().token(BOT_TOKEN).build()
        logger.debug("Application created")

        application.add_handler(CommandHandler("start", start))
        logger.debug("Start handler registered")

        for handler in ADMIN_HANDLERS:
            application.add_handler(handler)
        logger.debug(f"Registered {len(ADMIN_HANDLERS)} admin handlers")

        for handler in USER_HANDLERS:
            application.add_handler(handler)
        logger.debug(f"Registered {len(USER_HANDLERS)} user handlers")

        logger.info("Starting polling...")
        application.run_polling()
        logger.info("Polling started")

    except Exception as e:
        logger.critical(f"Application failed: {e}", exc_info=True)
        sys.exit(1)

print("اتاببیلیبلیبیبن")
if __name__ == "__main__":
    logger.info("Bot is starting...")
    main()