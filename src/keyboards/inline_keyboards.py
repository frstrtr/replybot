from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_tourism_main_inline_keyboard():
    """
    Возвращает основную встроенную клавиатуру для туристического бота с измененным порядком кнопок.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Ряд 1: Цены | ЧаВо
            [InlineKeyboardButton(text="💰 Цены", callback_data="prices"),
             InlineKeyboardButton(text="❓ ЧаВо", callback_data="faq")],
            # Ряд 2: Экскурсии | Контакты
            [InlineKeyboardButton(text="🗺️ Экскурсии", callback_data="excursions"),
             InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
            # Ряд 3: Лодки | Рыбалка
            [InlineKeyboardButton(text="🚤 Лодки", callback_data="boats"),
             InlineKeyboardButton(text="🎣 Рыбалка", callback_data="fishing")],
            # Ряд 4: Серфинг | Виндсерфинг & Кайтсерфинг
            [InlineKeyboardButton(text="🐳 Киты & Дельфины", callback_data="whales"),
             InlineKeyboardButton(text="🏄 Винд Кайт & Cёрфинг", callback_data="surfing")],
            # Ряд 5: Отзывы | О нас
            [InlineKeyboardButton(text="⭐ Отзывы", callback_data="reviews"),
             InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")],
            # Ряд 6: Поддержка | Помощь
            [InlineKeyboardButton(text="🛠️ Поддержка", callback_data="support"),
             InlineKeyboardButton(text="🆘 Помощь", callback_data="help")],
            # Ряд 7: Назад | Главное меню
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
             InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )


def get_back_to_main_menu_keyboard():
    """
    Возвращает клавиатуру с кнопками "Назад" и "Главное меню".
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
    )