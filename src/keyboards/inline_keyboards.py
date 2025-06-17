from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_tourism_main_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Часто Задаваемые Вопросы", callback_data="faq"),
             InlineKeyboardButton(text="Цены", callback_data="prices")],
            [InlineKeyboardButton(text="Контакты", callback_data="contacts"),
             InlineKeyboardButton(text="Экскурсии", callback_data="excursions")]
        ]
    )