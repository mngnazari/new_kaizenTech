# handlers/user_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ایمپورت‌های دیتابیس
from db.db import SessionLocal
from db.crud import get_user_by_telegram_id, get_tasks_by_staff_id, get_task_by_id # New import: get_task_by_id

# Import STAFF_KEYBOARD from keyboards.py
from keyboards import STAFF_KEYBOARD

async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the staff's tasks as inline keyboard buttons."""
    user_telegram_id = update.effective_user.id
    db = SessionLocal()
    try:
        staff_db = get_user_by_telegram_id(db, user_telegram_id)
        if not staff_db or staff_db.role != "staff":
            await update.message.reply_text("شما دسترسی به این بخش ندارید.")
            return

        tasks_for_staff = get_tasks_by_staff_id(db, staff_db.id)
        keyboard_buttons = []

        if tasks_for_staff:
            for task in tasks_for_staff:
                # Button for each task
                keyboard_buttons.append([InlineKeyboardButton(f"📄 {task.title}", callback_data=f"staff_view_task_{task.id}")])
        else:
            # If no tasks, just a message. No button for "no tasks"
            await update.message.reply_text("⏳ کاری برای شما تعریف نشده است.", reply_markup=STAFF_KEYBOARD)
            return

        # Create inline keyboard
        tasks_keyboard = InlineKeyboardMarkup(keyboard_buttons)

        # Send message with inline keyboard. User wants only the keyboard, so minimal text.
        await update.message.reply_text(
            "کارهای شما:", # A small header for context
            reply_markup=tasks_keyboard
        )

    finally:
        db.close()

async def staff_task_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles staff's click on a specific task button."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    task_id_str = callback_data.replace("staff_view_task_", "")
    try:
        task_id = int(task_id_str)
        # Create a single button for "اطلاعات کار"
        info_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("اطلاعات کار", callback_data=f"show_task_details_{task_id}")]])

        await query.edit_message_text(
            "برای مشاهده جزئیات، دکمه زیر را لمس کنید:",
            reply_markup=info_keyboard
        )
    except ValueError:
        await query.edit_message_text("⚠️ خطایی در شناسایی آیدی کار رخ داد.")


async def show_staff_task_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays full details of a selected task to the staff."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    task_id_str = callback_data.replace("show_task_details_", "")
    db = SessionLocal()
    try:
        task_id = int(task_id_str)
        task = get_task_by_id(db, task_id)

        if task:
            details_message = (
                f"📋 *عنوان کار*: {task.title}\n"
                f"⏰ *زمان تخمینی*: {task.time_estimate if task.time_estimate else 'تعریف نشده'}\n"
                f"🔥 *اولویت*: {task.priority if task.priority else 'تعریف نشده'}\n"
                f"📝 *نتایج مورد انتظار*: {task.expected_results if task.expected_results else 'تعریف نشده'}\n"
                f"⚡️ *وضعیت*: {task.status}\n"
                f"🗓 *تاریخ تعریف*: {task.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            await query.edit_message_text(details_message, parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ کار مورد نظر یافت نشد.")
    except ValueError:
        await query.edit_message_text("⚠️ خطایی در شناسایی آیدی کار رخ داد.")
    finally:
        db.close()


USER_HANDLERS = [
    MessageHandler(filters.Regex(r"^کیوبرد نیرو$"), staff_command),
    CallbackQueryHandler(staff_task_selected_callback, pattern=r"^staff_view_task_\d+$"),
    CallbackQueryHandler(show_staff_task_details, pattern=r"^show_task_details_\d+$"),
]