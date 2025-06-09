import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN, ADMIN, STAFFS
    from utils import create_staff_keyboard
    from keyboards import STAFF_KEYBOARD
    from handlers.admin_handler import ADMIN_HANDLERS
    from handlers.user_handler import USER_HANDLERS

    logger.info("All imports successful!")
    logger.info(f"BOT_TOKEN: {BOT_TOKEN[:5]}...")
    logger.info(f"ADMIN: {ADMIN}")
    logger.info(f"STAFFS: {STAFFS}")
    logger.info(f"ADMIN_HANDLERS: {len(ADMIN_HANDLERS)} handlers")
    logger.info(f"USER_HANDLERS: {len(USER_HANDLERS)} handlers")

    # تست تابع کیبورد
    keyboard = create_staff_keyboard(STAFFS)
    logger.info(f"Keyboard layout: {keyboard}")

except ImportError as e:
    logger.error(f"Import error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")