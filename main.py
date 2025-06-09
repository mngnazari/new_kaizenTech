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

# ایمپورت‌های مربوط به دیتابیس (مسیرهای جدید)
from db.db import init_db, SessionLocal  # تغییر اینجا
from db.crud import get_user_by_telegram_id, get_staff_members_of_admin, init_users_and_staffs # تغییر اینجا
from config import BOT_TOKEN, ADMIN

try:
    from utils import create_staff_keyboard
    from handlers.admin_handler import ADMIN_HANDLERS
    from handlers.user_handler import USER_HANDLERS
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
        try: # اضافه کردن try-finally برای اطمینان از بسته شدن سشن
            db_user = get_user_by_telegram_id(db, user_id)

            if user_id == ADMIN["id"]:
                logger.debug("Admin detected")
                admin_db_user = get_user_by_telegram_id(db, ADMIN["id"])
                if not admin_db_user or admin_db_user.role != "admin":
                    await update.message.reply_text("خطا: ادمین در دیتابیس یافت نشد یا نقش آن صحیح نیست.")
                    return

                staffs_from_db = get_staff_members_of_admin(db, admin_db_user.id)
                staffs_for_keyboard = [{"id": s.telegram_id, "name": s.name} for s in staffs_from_db]

                staff_inline_keyboard = create_staff_keyboard(staffs_for_keyboard)

                staff_list = "\n".join([f"- {staff.name} (آیدی: `{staff.telegram_id}`)" for staff in staffs_from_db])
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

            elif db_user and db_user.role == "staff":
                logger.debug("Staff member detected")
                await update.message.reply_text(
                    "سلام نیروی محترم!",
                    reply_markup=STAFF_KEYBOARD
                )
                logger.info("Staff welcome message sent")

            else:
                logger.debug("Regular user detected")
                if not db_user:
                    user_full_name = user.full_name if user.full_name else f"کاربر {user_id}"
                    create_user(db, user_id, user_full_name, "user") # create_user باید ایمپورت شود اگر استفاده می شود
                    logger.info(f"New user {user_id} added to DB with role 'user'.")

                await update.message.reply_text("سلام کاربر عزیز!")
                logger.info("Regular user welcome message sent")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)


def main() -> None:
    try:
        logger.info("Initializing database...")
        init_db()
        db = SessionLocal()
        try: # اضافه کردن try-finally برای اطمینان از بسته شدن سشن
            init_users_and_staffs(db)
        finally:
            db.close()
        logger.info("Database initialization complete.")

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


if __name__ == "__main__":
    logger.info("Bot is starting...")
    main()