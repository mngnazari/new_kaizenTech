from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

# ایمپورت STAFFS و ADMIN از فایل config
from config import STAFFS, ADMIN

# ایمپورت‌های دیتابیس
from db.db import SessionLocal
from db.crud import get_user_by_telegram_id, create_task, get_staff_members_of_admin, create_user, get_tasks_by_staff_id

# Stateهای برای ConversationHandler
TITLE, TIME, PRIORITY, EXPECTED_RESULTS = range(4)


# توابع placeholder برای admin_command و cube_admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شما وارد بخش مدیریت شدید!")

async def cube_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("منوی کیوب ادمین در حال آماده‌سازی است...")


# تابع برای نمایش کیبورد عملیات نیرو (با دکمه اضافه کردن کار جدید و کارهای موجود)
# admin_handler.py

# ... (بقیه کدها دست نخورده)

# تابع برای نمایش کیبورد عملیات نیرو (با دکمه اضافه کردن کار جدید و کارهای موجود)
async def show_staff_operations_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, staff_telegram_id: int):
    db = SessionLocal()
    try:
        staff_db = get_user_by_telegram_id(db, staff_telegram_id)
        if not staff_db or staff_db.role != "staff":
            if update.callback_query:
                await update.callback_query.edit_message_text("⚠️ نیرو انتخاب شده نامعتبر است.")
            else:
                await update.message.reply_text("⚠️ نیرو انتخاب شده نامعتبر است.")
            return

        keyboard_buttons = []

        tasks_for_staff = get_tasks_by_staff_id(db, staff_db.id)
        if tasks_for_staff:
            for task in tasks_for_staff:
                keyboard_buttons.append([InlineKeyboardButton(f"📄 {task.title}", callback_data=f"view_task_{task.id}")])

        keyboard_buttons.append(
            [InlineKeyboardButton("➕ اضافه کردن کار جدید", callback_data=f"add_new_task_{staff_telegram_id}")]
        )

        keyboard_buttons.append(
            [InlineKeyboardButton("بازگشت به لیست نیروها", callback_data="back_to_staff_list")]
        )

        staff_operations_keyboard = InlineKeyboardMarkup(keyboard_buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                ".", # <--- تغییر اینجا: استفاده از یک نقطه به جای فضای خالی
                reply_markup=staff_operations_keyboard,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                ".", # <--- تغییر اینجا: استفاده از یک نقطه به جای فضای خالی
                reply_markup=staff_operations_keyboard,
                parse_mode="Markdown"
            )
    finally:
        db.close()

# ... (بقیه کدها دست نخورده)

# تابع برای مدیریت انتخاب نیرو از کیبورد شیشه‌ای
async def select_staff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data.startswith("select_staff_"):
        staff_id_str = callback_data.replace("select_staff_", "")
        try:
            selected_staff_telegram_id = int(staff_id_str)
            context.user_data['selected_staff_telegram_id'] = selected_staff_telegram_id
            await show_staff_operations_keyboard(update, context, selected_staff_telegram_id)

        except ValueError:
            await query.edit_message_text("⚠️ خطایی در شناسایی آیدی نیرو رخ داد.")

    elif callback_data == "manage_staffs":
        await query.edit_message_text(
            "منوی مدیریت نیروها در حال آماده‌سازی است...",
            reply_markup=ReplyKeyboardRemove()
        )
    elif callback_data == "back_to_staff_list":
        # بازگشت به لیست نیروها
        from utils import create_staff_keyboard
        db = SessionLocal()
        try:
            admin_db_user = get_user_by_telegram_id(db, ADMIN["id"])
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
            await query.edit_message_text(
                message,
                reply_markup=staff_inline_keyboard,
                parse_mode="Markdown"
            )
        finally:
            db.close()
    elif callback_data.startswith("view_task_"):
        task_id_str = callback_data.replace("view_task_", "")
        try:
            task_id = int(task_id_str)
            # در اینجا می‌توانید جزئیات کار را از دیتابیس بگیرید و نمایش دهید.
            # فعلاً فقط یک پیام موقت:
            await query.edit_message_text(f"شما کار با آیدی {task_id} را انتخاب کردید. (جزئیات کار نمایش داده می‌شود)")
            # نکته: اگر میخواهید پس از نمایش جزئیات کار، دوباره کیبورد عملیات نیرو نمایش داده شود:
            # selected_staff_telegram_id = context.user_data.get('selected_staff_telegram_id')
            # if selected_staff_telegram_id:
            #     await show_staff_operations_keyboard(update, context, selected_staff_telegram_id)
        except ValueError:
            await query.edit_message_text("⚠️ خطایی در شناسایی آیدی کار رخ داد.")


# توابع برای ConversationHandler اضافه کردن کار جدید
async def start_add_new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # مهم: برای جلوگیری از نمایش لودینگ روی دکمه

    if 'selected_staff_telegram_id' not in context.user_data:
        await query.edit_message_text("خطا: نیرویی انتخاب نشده است. لطفا دوباره شروع کنید.")
        return ConversationHandler.END

    selected_staff_telegram_id = context.user_data['selected_staff_telegram_id']
    db = SessionLocal()
    try:
        staff = get_user_by_telegram_id(db, selected_staff_telegram_id)
        if staff and staff.role == "staff":
            # ویرایش پیام قبلی با یک پیام جدید برای شروع محاوره
            await query.edit_message_text(f"شما در حال اضافه کردن کار برای نیرو *{staff.name}* هستید.\n\nلطفا عنوان کار را وارد کنید:", parse_mode="Markdown")
            # نیازی به reply_text جدید نیست، چون edit_message_text را انجام دادیم.
            return TITLE
        else:
            await query.edit_message_text("خطا: نیروی انتخاب شده نامعتبر است.")
            return ConversationHandler.END
    finally:
        db.close()


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_task_title'] = update.message.text
    await update.message.reply_text("لطفا زمان انجام کار را وارد کنید (مثال: 2 ساعت):")
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_task_time'] = update.message.text
    await update.message.reply_text("لطفا اولویت کار را وارد کنید (مثال: بالا، متوسط، پایین):")
    return PRIORITY

async def get_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_task_priority'] = update.message.text
    await update.message.reply_text("لطفا نتایج مورد انتظار را وارد کنید:")
    return EXPECTED_RESULTS

async def get_expected_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_task_expected_results'] = update.message.text

    selected_staff_telegram_id = context.user_data.get('selected_staff_telegram_id')
    db = SessionLocal()
    try:
        staff_db_object = get_user_by_telegram_id(db, selected_staff_telegram_id)

        if staff_db_object and staff_db_object.role == "staff":
            new_task = create_task(
                db=db,
                title=context.user_data.get('new_task_title'),
                time_estimate=context.user_data.get('new_task_time'),
                priority=context.user_data.get('new_task_priority'),
                expected_results=context.user_data.get('new_task_expected_results'),
                assigned_staff_id=staff_db_object.id
            )
            staff_name = staff_db_object.name
            summary = (
                f"✅ کار جدید برای نیرو {staff_name} با موفقیت ثبت شد:\n"
                f"(آیدی کار در دیتابیس: {new_task.id})\n\n"
                f"عنوان کار: {new_task.title}\n"
                f"زمان انجام: {new_task.time_estimate}\n"
                f"اولویت: {new_task.priority}\n"
                f"نتایج مورد انتظار: {new_task.expected_results}\n\n"
            )
            await update.message.reply_text(summary)
            # پس از ثبت کار، مجدداً کیبورد عملیات نیرو را نمایش دهید تا کار جدید دیده شود
            await show_staff_operations_keyboard(update, context, selected_staff_telegram_id)
        else:
            await update.message.reply_text("⚠️ خطایی در ذخیره کار رخ داد: نیروی مربوطه یافت نشد.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ خطایی در ذخیره کار رخ داد: {e}")
        print(f"Error saving task: {e}")
    finally:
        db.close()

    return ConversationHandler.END

async def cancel_add_new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات اضافه کردن کار جدید لغو شد.")
    selected_staff_telegram_id = context.user_data.get('selected_staff_telegram_id')
    if selected_staff_telegram_id:
        await show_staff_operations_keyboard(update, context, selected_staff_telegram_id)
    return ConversationHandler.END


add_task_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_new_task, pattern=r"^add_new_task_\d+$")],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        PRIORITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_priority)],
        EXPECTED_RESULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expected_results)],
    },
    fallbacks=[CommandHandler("cancel", cancel_add_new_task)],
    allow_reentry=True
)


ADMIN_HANDLERS = [
    CommandHandler("admin", admin_command),
    MessageHandler(filters.Regex(r"^کیوبدرادمین$"), cube_admin),
    add_task_conversation_handler, # <--- انتقال این هندلر به بالای لیست
    # الگوی CallbackQueryHandler برای select_staff_callback باید add_new_task_\d+ را شامل نشود
    CallbackQueryHandler(select_staff_callback, pattern=r"^(select_staff_\d+|manage_staffs|back_to_staff_list|view_task_\d+|ignore)$"),
]