"""
Centralized configuration for bot menus.
This allows for easy creation of multi-layered menus and assignment
of different menu structures to different business clients.
"""
import config as app_config

# --- Define the structure for a default menu ---
# This is a template that can be reused or used as a fallback.
DEFAULT_MENU_STRUCTURE = {
    # --- Main Menu Nodes ---
    "main_menu": {
        "type": "menu",
        "text": "Пожалуйста, выберите нужный вопрос ниже или задайте свой.",
        "buttons": [
            [{"text": "💰 Цены", "target": "prices"}, {"text": "❓ ЧаВо", "target": "faq"}],
            [{"text": "🚤 Лодки", "target": "boats_menu"}, {"text": "🗺️ Экскурсии", "target": "excursions"}],
            [{"text": "🎣 Рыбалка", "target": "fishing"}, {"text": "⭐ Отзывы", "target": "reviews"}],
            [{"text": "ℹ️ О нас", "target": "about"}, {"text": "📞 Контакты", "target": "contacts"}],
            [{"text": "🆘 Помощь", "target": "help"}],
        ]
    },
    "boats_menu": {
        "type": "menu",
        "text": "Выберите тип лодки:",
        "buttons": [
            [{"text": "Sea Strike 52 Ft", "target": "boat1"}, {"text": "TORa 54 Ft", "target": "boat2"}],
            [{"text": "Mercury 17 Ft", "target": "boat3"}, {"text": "Catamaran 40 Ft", "target": "boat4"}],
            [{"text": "Yamaha 1 Red", "target": "boat5"}, {"text": "LIMITLESS fishing", "target": "boat6"}],
            [{"text": "Benetau GT 40", "target": "boat7"}, {"text": "Benetau GT 38", "target": "boat8"}],
            [{"text": "Yamaha 2 Blue", "target": "boat9"}, {"text": "Scarab 255 LX Wake", "target": "boat10"}],
            [{"text": "Saxdor 270", "target": "boat11"},],
            [{"text": "⬅️ Назад", "target": "main_menu"}]
        ]
    },

    # --- Content Nodes (pointing to HTML files) ---
    # The `text_path` is relative. The final path will be constructed as:
    # static/responses/<business_connection_id>/<text_path>
    "prices":     {"type": "content", "text_path": "prices.html", "back_to": "main_menu"},
    "faq":        {"type": "content", "text_path": "faq.html", "back_to": "main_menu"},
    "excursions": {"type": "content", "text_path": "excursions.html", "back_to": "main_menu"},
    "fishing":    {"type": "content", "text_path": "fishing.html", "file_id": "https://t.me/mauritiusTransfer/3427", "back_to": "main_menu"},
    "reviews":    {"type": "content", "text_path": "reviews.html", "back_to": "main_menu"},
    "about":      {"type": "content", "text_path": "about.html", "back_to": "main_menu"},
    "contacts":   {"type": "content", "text_path": "contacts.html", "back_to": "main_menu"},
    "help":       {"type": "content", "text_path": "help.html", "is_final": True}, # 'is_final' removes all buttons

    "boat1":      {"type": "content", "text_path": "boat1.html", "back_to": "boats_menu"},
    "boat2":      {"type": "content", "text_path": "boat2.html", "back_to": "boats_menu"},
    "boat3":      {"type": "content", "text_path": "boat3.html", "back_to": "boats_menu"},
    "boat4":      {"type": "content", "text_path": "boat4.html", "back_to": "boats_menu"},
    "boat5":      {"type": "content", "text_path": "boat5.html", "back_to": "boats_menu"},
    "boat6":      {"type": "content", "text_path": "boat6.html", "back_to": "boats_menu"},
    "boat7":      {"type": "content", "text_path": "boat7.html", "back_to": "boats_menu"},
    "boat8":      {"type": "content", "text_path": "boat8.html", "back_to": "boats_menu"},
    "boat9":      {"type": "content", "text_path": "boat9.html", "back_to": "boats_menu"},
    "boat10":      {"type": "content", "text_path": "boat10.html", "back_to": "boats_menu"},
    "boat11":      {"type": "content", "text_path": "boat11.html", "back_to": "boats_menu"},
}

# --- Client-Specific Menu Assignments ---
# Map a business_connection_id to a specific menu structure.
CLIENT_MENUS = {
    # Example for the hardcoded client from your config file
    app_config.HC_BUSINESS_CONNECTION_ID: DEFAULT_MENU_STRUCTURE,
    
    # Example for another client with a completely different menu
    # "another_business_connection_id": ANOTHER_MENU_STRUCTURE,
}

def get_menu_for_client(business_connection_id: str) -> dict:
    """
    Returns the menu structure for a given client ID.
    Falls back to the default menu if the client is not specifically configured.
    """
    return CLIENT_MENUS.get(business_connection_id, DEFAULT_MENU_STRUCTURE)