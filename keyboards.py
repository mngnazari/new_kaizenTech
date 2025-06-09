from telegram import ReplyKeyboardMarkup

# فقط کیبورد نیروها باقی می‌ماند
STAFF_KEYBOARD = ReplyKeyboardMarkup(
    [["کیوبرد نیرو"]],
    resize_keyboard=True,
    is_persistent=True
)