import logging
import sys
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# تنظیمات پیشرفته لاگ‌گیری
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN, ADMIN, STAFFS
    from utils import create_staff_keyboard
    from handlers.admin_handler import ADMIN_HANDLERS
    from handlers.user_handler import USER_HANDLERS, staff_command # <-- اضافه شدن staff_command
    from db.db import init_db, SessionLocal
    from db.crud import init_users_and_staffs, get_user_by_telegram_id, get_staff_members_of_admin
    from keyboards import STAFF_KEYBOARD
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

        db = SessionLocal()
        try:
            db_user = get_user_by_telegram_id(db, user_id)
            if not db_user:
                init_users_and_staffs(db)
                if user_id != ADMIN["id"] and user_id not in [s["id"] for s in STAFFS]:
                     from db.crud import create_user
                     create_user(db, user_id, user.full_name, role="user")
                     db_user = get_user_by_telegram_id(db, user_id)

            if db_user.role == "admin":
                logger.debug("Admin detected")
                staffs_from_db = get_staff_members_of_admin(db, db_user.id)
                staffs_for_keyboard = [{"id": s.telegram_id, "name": s.name} for s in staffs_from_db]
                staff_inline_keyboard = create_staff_keyboard(staffs_for_keyboard)

                staff_list = "\n".join([f"- {staff.name} (آیدی: `{staff.telegram_id}`)" for staff in staffs_from_db])
                message = (
                    f"سلام {db_user.name} عزیز، ادمین گرامی!\n\n"
                    "لیست نیروهای شما:\n"
                    f"{staff_list}\n\n"
                    "لطفا یکی از نیروها را انتخاب کنید:"
                )
                await update.message.reply_text(
                    message,
                    reply_markup=staff_inline_keyboard,
                    parse_mode="Markdown"
                )
                logger.info("Admin welcome message sent with staff list")

            elif db_user.role == "staff":
                logger.debug("Staff detected. Calling staff_command to show tasks.")
                # <--- تغییر مهم در این قسمت --->
                # به جای ارسال یک پیام ثابت، تابع staff_command را فراخوانی می‌کنیم
                # staff_command هم ReplyKeyboardMarkup (کیوبرد نیرو) را می‌دهد
                # و هم InlineKeyboardMarkup (لیست کارها) را در پیام بعدی.
                await staff_command(update, context) # فراخوانی تابع از user_handler.py
                logger.info("Staff welcome message and tasks sent via staff_command")

            else:
                logger.debug("Regular user detected")
                await update.message.reply_text("سلام کاربر عزیز!")
                logger.info("Regular user welcome message sent")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)


def main() -> None:
    try:
        logger.info("Starting bot application...")
        application = Application.builder().token(BOT_TOKEN).build()
        logger.debug("Application created")

        logger.info("Initializing database...")
        init_db()
        db_session = SessionLocal()
        try:
            init_users_and_staffs(db_session)
        finally:
            db_session.close()

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

if __name__ == "__main__":
    main()