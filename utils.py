from telegram import InlineKeyboardButton, InlineKeyboardMarkup # اضافه شد

def create_staff_keyboard(staffs):
    """
    ایجاد کیبورد شیشه‌ای برای نیروها با طراحی زیبا
    هر ردیف حداکثر 2 دکمه خواهد داشت
    """
    keyboard = []
    row = []

    for i, staff in enumerate(staffs):
        # استفاده از نام نیرو برای دکمه و آیدی نیرو برای callback_data
        row.append(InlineKeyboardButton(staff["name"], callback_data=f"select_staff_{staff['id']}")) # تغییر اینجا

        # هر دو نیرو در یک ردیف قرار می‌گیرند
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []

    # اضافه کردن ردیف آخر اگر خالی نباشد
    if row:
        keyboard.append(row)

    # اضافه کردن دکمه مدیریت در ردیف آخر
    # برای مدیریت نیروها نیز می‌توانیم از callback_data استفاده کنیم
    keyboard.append([InlineKeyboardButton("مدیریت نیروها", callback_data="manage_staffs")]) # تغییر اینجا

    return InlineKeyboardMarkup(keyboard) # تغییر اینجا