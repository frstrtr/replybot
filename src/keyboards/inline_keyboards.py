from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_keyboard_from_config(buttons_config: list[list[dict]]) -> InlineKeyboardMarkup:
    """
    Builds an InlineKeyboardMarkup from a nested list of button configurations.
    
    :param buttons_config: A list of lists, where each inner list is a row of buttons.
                           Each button is a dict with "text" and "target" (callback_data).
    :return: An InlineKeyboardMarkup object.
    """
    keyboard_rows = []
    for row_config in buttons_config:
        row = [
            InlineKeyboardButton(text=button["text"], callback_data=button["target"])
            for button in row_config
        ]
        keyboard_rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


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


def get_back_to_main_menu_keyboard(back_callback_data="main_menu"):
    """
    Возвращает клавиатуру с кнопками "Назад" и "Главное меню".
    back_callback_data: callback_data для кнопки "Назад"
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
    )


def get_boats_submenu_keyboard():
    """
    Возвращает клавиатуру для подменю лодок.
    """
    boats_rows = [
        [InlineKeyboardButton(text="🚤 boat1", callback_data="boat1"), InlineKeyboardButton(text="🛥️ boat2", callback_data="boat2")],
        [InlineKeyboardButton(text="⛵ boat3", callback_data="boat3"), InlineKeyboardButton(text="🛶 boat4", callback_data="boat4")],
    ]
    back_menu_row = get_back_to_main_menu_keyboard(back_callback_data="main_menu").inline_keyboard[0]
    return InlineKeyboardMarkup(
        inline_keyboard=boats_rows + [back_menu_row]
    )