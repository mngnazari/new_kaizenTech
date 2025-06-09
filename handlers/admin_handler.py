from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

# ایمپورت STAFFS از فایل config
from config import STAFFS

# Stateهای برای ConversationHandler
TITLE, TIME, PRIORITY, EXPECTED_RESULTS = range(4) # تعریف Stateها


# توابع placeholder برای admin_command و cube_admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شما وارد بخش مدیریت شدید!")

async def cube_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("منوی کیوب ادمین در حال آماده‌سازی است...")


# تابع برای نمایش کیبورد عملیات نیرو (با دکمه اضافه کردن کار جدید)
async def show_staff_operations_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, staff_id: int):
    # این کیبورد شیشه‌ای جدید است که برای هر نیرو باز می‌شود
    staff_operations_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ اضافه کردن کار جدید", callback_data=f"add_new_task_{staff_id}")],
        [InlineKeyboardButton("بازگشت به لیست نیروها", callback_data="back_to_staff_list")]
    ])

    staff = next((s for s in STAFFS if s["id"] == staff_id), None)
    if staff:
        response = (
            f"👤 نیرو: {staff['name']}\n"
            f"🆔 آیدی: `{staff['id']}`\n\n"
            "لطفا عملیات مورد نظر را انتخاب کنید:"
        )
        # این مطمئن می‌شود که پیام از callback_query یا message اصلی گرفته شود
        if update.callback_query:
            await update.callback_query.edit_message_text(
                response,
                reply_markup=staff_operations_keyboard,
                parse_mode="Markdown"
            )
        else: # برای مواردی که از یک پیام معمولی به اینجا هدایت می‌شویم
            await update.message.reply_text(
                response,
                reply_markup=staff_operations_keyboard,
                parse_mode="Markdown"
            )
    else:
        if update.callback_query:
            await update.callback_query.edit_message_text("⚠️ نیرو انتخاب شده نامعتبر است.")
        else:
            await update.message.reply_text("⚠️ نیرو انتخاب شده نامعتبر است.")


# تابع برای مدیریت انتخاب نیرو از کیبورد شیشه‌ای
async def select_staff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data.startswith("select_staff_"):
        staff_id_str = callback_data.replace("select_staff_", "")
        try:
            selected_staff_id = int(staff_id_str)
            # ذخیره آیدی نیروی انتخاب شده در context.user_data برای استفاده‌های بعدی
            context.user_data['selected_staff_id'] = selected_staff_id
            await show_staff_operations_keyboard(update, context, selected_staff_id)

        except ValueError:
            await query.edit_message_text("⚠️ خطایی در شناسایی آیدی نیرو رخ داد.")

    elif callback_data == "manage_staffs":
        await query.edit_message_text(
            "منوی مدیریت نیروها در حال آماده‌سازی است...",
            reply_markup=ReplyKeyboardRemove()
        )
    elif callback_data == "back_to_staff_list":
        # بازگشت به لیست نیروها (همان کاری که /start انجام می‌دهد)
        from utils import create_staff_keyboard # این ایمپورت باید در بالای فایل باشد یا در جایی که نیاز است
        staff_inline_keyboard = create_staff_keyboard(STAFFS)
        staff_list = "\n".join([f"- {staff['name']} (آیدی: {staff['id']})" for staff in STAFFS])
        message = (
            f"سلام {ADMIN['name']} عزیز، ادمین گرامی!\n\n" # استفاده از ADMIN['name'] از config
            "لیست نیروهای شما:\n"
            f"{staff_list}\n\n"
            "لطفا یکی از نیروها را انتخاب کنید:"
        )
        await query.edit_message_text(
            message,
            reply_markup=staff_inline_keyboard,
            parse_mode="Markdown"
        )


# توابع برای ConversationHandler اضافه کردن کار جدید
async def start_add_new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # اطمینان حاصل کنید که selected_staff_id در context.user_data موجود است
    if 'selected_staff_id' not in context.user_data:
        await query.edit_message_text("خطا: نیرویی انتخاب نشده است. لطفا دوباره شروع کنید.")
        return ConversationHandler.END

    selected_staff_id = context.user_data['selected_staff_id']
    staff = next((s for s in STAFFS if s["id"] == selected_staff_id), None)
    if staff:
        # پیام قبلی را ویرایش می کند و سوال اول را می پرسد
        await query.edit_message_text(f"شما در حال اضافه کردن کار برای نیرو {staff['name']} هستید.")
        await query.message.reply_text("لطفا عنوان کار را وارد کنید:") # پیام جدید برای سوال
        return TITLE
    else:
        await query.edit_message_text("خطا: نیروی انتخاب شده نامعتبر است.")
        return ConversationHandler.END

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

    selected_staff_id = context.user_data.get('selected_staff_id')
    staff = next((s for s in STAFFS if s["id"] == selected_staff_id), None)
    staff_name = staff['name'] if staff else "نامعلوم"

    summary = (
        f"✅ کار جدید برای نیرو {staff_name} با موفقیت ثبت شد:\n\n"
        f"عنوان کار: {context.user_data.get('new_task_title')}\n"
        f"زمان انجام: {context.user_data.get('new_task_time')}\n"
        f"اولویت: {context.user_data.get('new_task_priority')}\n"
        f"نتایج مورد انتظار: {context.user_data.get('new_task_expected_results')}\n\n"
        "این اطلاعات بعدا در دیتابیس ذخیره خواهد شد."
    )
    await update.message.reply_text(summary)

    # پایان محاوره
    return ConversationHandler.END

async def cancel_add_new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات اضافه کردن کار جدید لغو شد.")
    # نمایش دوباره کیبورد عملیات نیرو
    selected_staff_id = context.user_data.get('selected_staff_id')
    if selected_staff_id:
        await show_staff_operations_keyboard(update, context, selected_staff_id)
    return ConversationHandler.END


# به روزرسانی هندلرها
# ConversationHandler برای اضافه کردن کار جدید
add_task_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_new_task, pattern=r"^add_new_task_\d+$")],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        PRIORITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_priority)],
        EXPECTED_RESULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expected_results)],
    },
    fallbacks=[CommandHandler("cancel", cancel_add_new_task)], # قابلیت لغو
    allow_reentry=True # اجازه ورود مجدد به محاوره
)


ADMIN_HANDLERS = [
    CommandHandler("admin", admin_command),
    MessageHandler(filters.Regex(r"^کیوبدرادمین$"), cube_admin),
    # الگوی جدید برای پوشش callback_dataهای شامل آیدی
    CallbackQueryHandler(select_staff_callback, pattern=r"^(select_staff_\d+|manage_staffs|back_to_staff_list)$"),
    add_task_conversation_handler, # اضافه کردن ConversationHandler جدید
]