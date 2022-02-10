from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

# Login Keyboard
contact_keyboard = KeyboardButton('Войти', request_contact=True)
custom_keyboard_login = [[contact_keyboard]]
REPLY_KEYBOARD_MARKUP = ReplyKeyboardMarkup(custom_keyboard_login, resize_keyboard=True)

REPLY_BACK_MENU_FROM_PHOTO = '⬅️ Назад'
back_menu_fp_keyboard = KeyboardButton(REPLY_BACK_MENU_FROM_PHOTO)
back_menu_fp_login = [[back_menu_fp_keyboard]]
REPLY_BACK_TO_MENU_FROM_PHOTO = ReplyKeyboardMarkup(back_menu_fp_login, resize_keyboard=True)

# <editor-fold desc="Consts">

CALLBACK_ANKET_GIRL = "cb_anket_girl"
CALLBACK_ANKET_BOY = "cb_anket_boy"
CALLBACK_ANKET_ANOTHER = "cb_anket_another"

CALLBACK_ANKET_PARTN_GIRL = "cb_anket_partner_girl"
CALLBACK_ANKET_PARTN_BOY = "cb_anket_partner_boy"
CALLBACK_ANKET_PARTN_DOUBLE = "cb_anket_partner_another"

CALLBACK_ANKET_AGE_1 = "cb_anket_sc"
CALLBACK_ANKET_AGE_2 = "cb_anket_bc"

CALLBACK_ANKET_CONFIRM = "cb_anket_conf"
CALLBACK_ANKET_DECONF = "cd_anket_deconf"

CALLBACK_OPEN_SEARCH = "cb_open_sch"
CALLBACK_EDIT_MY_DATA = "cb_edit_my_data"
CALLBACK_ADD_PHOTO = "cb_add_photo"
CALLBACK_WEB_VALENTINE = "cb_web_valentine"
CALLBACK_CINEMA_NIGHT = "cb_cinema_night"
CALLBACK_MUSIC = "cb_music"
CALLBACK_AUTHORS = "cb_authors"

CALLBACK_START_SEARCH = "cb_start_sch"
CALLBACK_STOP_SEARCH = "cb_stop_search"

CALLBACK_BACK_MAIN_MENU = "cb_back_mm"

CALLBACK_RE_SEARCH = "cb_re_search"
CALLBACK_RETURN_TO_MAIN_MENU_FROM_CHAT = "cb_ret_to_mm_fr_ch"

CALLBACK_RANDOM_QUESTION = "cb_random_question"

CALLBACK_BACK_FROM_PHOTO_EDIT = "cb_back_from_photo_edit"



# Main Menu
def get_main_menu(): 
    keyboard = [
        [
            InlineKeyboardButton("🔍 Начать поиск! 💞️", callback_data=CALLBACK_OPEN_SEARCH),
        ],
        [
            InlineKeyboardButton("📝 Изменить данные", callback_data=CALLBACK_EDIT_MY_DATA),
            InlineKeyboardButton("📸 Добавить Фото", callback_data=CALLBACK_ADD_PHOTO),
        ],
        # [
        #     InlineKeyboardButton("🎥 Романтическая Кинополночь", callback_data=CALLBACK_CINEMA_NIGHT),
        # ],
        [
            InlineKeyboardButton("🎶 ART.HUB Radio", url='https://t.me/arthub_radio'),
        ],
        [
            InlineKeyboardButton("theHub.su", url='https://thehub.su/'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_start_search(gender):
    mes_text = "Я готова! ✨" if gender == 0 else "Я готов! 💪"
    keyboard = [
        [
            InlineKeyboardButton(" {}".format(mes_text), callback_data=CALLBACK_START_SEARCH),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data=CALLBACK_BACK_MAIN_MENU),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)


def get_stop_search():
    keyboard = [
        [
            InlineKeyboardButton("⛔️ Отменить поиск".format(), callback_data=CALLBACK_STOP_SEARCH),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cinemanight():
    keyboard = [
        [
            InlineKeyboardButton("HUB Discord", url="https://discord.gg/K72gj8vk"),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data=CALLBACK_BACK_MAIN_MENU),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_random_question():
    keyboard = [
        [
            InlineKeyboardButton("Случайный вопрос".format(), callback_data=CALLBACK_RANDOM_QUESTION),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Anket
def get_anket_gender():
    keyboard = [
        [
            InlineKeyboardButton(" Девушка", callback_data=CALLBACK_ANKET_GIRL),
        ],
        [
            InlineKeyboardButton(" Парень", callback_data=CALLBACK_ANKET_BOY),
        ],
        [
            InlineKeyboardButton(" Другим", callback_data=CALLBACK_ANKET_ANOTHER),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_anket_partner():
    keyboard = [
        [
            InlineKeyboardButton(" Парни", callback_data=CALLBACK_ANKET_PARTN_GIRL),
        ],
        [
            InlineKeyboardButton(" Девушки", callback_data=CALLBACK_ANKET_PARTN_BOY),
        ],
        [
            InlineKeyboardButton(" Оба", callback_data=CALLBACK_ANKET_PARTN_DOUBLE),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_anket_age():
    keyboard = [
        [
            InlineKeyboardButton("🍦 1-2 курс", callback_data=CALLBACK_ANKET_AGE_1),
        ],
        [
            InlineKeyboardButton("🍧 3-5 курс", callback_data=CALLBACK_ANKET_AGE_2),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)


def get_anket_confirm():
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=CALLBACK_ANKET_CONFIRM),
        ],
        [
            InlineKeyboardButton("❌ Изменить", callback_data=CALLBACK_ANKET_DECONF),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)


def re_search():
    keyboard = [
        [
            InlineKeyboardButton("💔 Нет, подобрать еще раз", callback_data=CALLBACK_RE_SEARCH),
        ],
        [
            InlineKeyboardButton("Выйти в меню", callback_data=CALLBACK_RETURN_TO_MAIN_MENU_FROM_CHAT),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def bad_re_search():
    keyboard = [
        [
            InlineKeyboardButton("Подобрать еще раз", callback_data=CALLBACK_START_SEARCH),
        ],
        [
            InlineKeyboardButton("Выйти в меню", callback_data=CALLBACK_BACK_MAIN_MENU),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_from_photo_edit():
    keyboard = [
        [
            InlineKeyboardButton("🔙 Назад", callback_data=CALLBACK_BACK_FROM_PHOTO_EDIT),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
