# Import # Telegram-bot-api 12.8.0      pymongo[srv]    Binary   PIL
from pymongo import MongoClient

import os

import cv2
import numpy

import telebot

import logging
import time
import random

from keyboard import *

from bot_config import TG_TOKEN
from bot_config import MONGODB_LINK
from bot_config import MONGO_DB

from telegram import Bot
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackContext

bot = telebot.TeleBot(TG_TOKEN, parse_mode=None)
# Connect to DataBase
mondb = MongoClient(MONGODB_LINK)[MONGO_DB]


def on_start(update: Update, context: CallbackContext):
    message = update.message
    user = mondb.Valentia22_users.find_one({"user_id": message.chat.id})
    logging.info(message.chat.id)
    if not user:
        message.reply_text(
            'Привет! Необходимо войти в систему!',
            reply_markup=REPLY_KEYBOARD_MARKUP
        )
    else:
        if user.get('anket_done') == False:
            message.reply_text(
                text="Внимание!\
                Все собираемые данные являются анонимными, не подлежат разглашению и будут уничтожены по окончанию Ивента",
            )
            message.reply_text(
                text="Для начала ответьте на несколько вопросов! \nВаш пол:",
                reply_markup=get_anket_gender()
            )
        else:
            message.reply_text(
                "Основное меню: ",
                reply_markup=get_main_menu()
            )

def comm_advert(update: Update, context: CallbackContext):
    ad = update.message.text
    user = mondb.users.find_one({"user_id": update.message.chat_id})
    if user['user_phone'] == 7072917226:
        for v_user in mondb.Valentia22_users.find():
            context.bot.send_message(
                chat_id=v_user.get("user_id"),
                text=ad[8:],
            )

def get_photo(update: Update, context: CallbackContext):
    user = mondb.Valentia22_users.find_one({"user_id": update.message.chat.id})
    query = update.callback_query
    if user.get('user_photo') is not None:
        if user.get('user_photo') == "need":
            fileID = update.message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("user_photos/" + str(user['user_id']) + ".jpg", 'wb') as new_file:
                new_file.write(downloaded_file)

            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_photo': "user_photos/" + str(user['user_id']) + ".jpg",
                          }
                 })

            context.bot.send_message(
                chat_id=user['user_id'],
                text="Фото успешно добавлено!",
                reply_markup=ReplyKeyboardRemove(),
            )
            context.bot.send_message(
                chat_id=user['user_id'],
                text="Главное меню:",
                reply_markup=get_main_menu(),
            )

# IF user message == contact
def on_contact(update: Update, context: CallbackContext):
    message = update.message
    user = mondb.Valentia22_users.find_one({"user_id": message.chat.id})
    user_phone_number = 0
    user_chat_id = 0
    # IF user get another Contact
    if message.chat_id == int(message.contact['user_id']):
        if message.contact:
            if user is None:
                num1 = str(message.contact['phone_number'])
                user_phone_number = 0

                for i in range(-10, 0):
                    user_phone_number += int(num1[i]) * (10 ** ((i + 1) * -1))
                user_chat_id += int(message.contact['user_id'])

                mondb.Valentia22_users.insert_one(
                    {'user_id': user_chat_id,
                     'user_phone': user_phone_number,
                     'anket_done': False,
                     'chat_history': " ",
                     'status': 0}
                )

                message.reply_text(
                    'Вы успешно авторизированы!',
                    reply_markup=ReplyKeyboardRemove()
                )
                anket_answer_start(message)
            elif not user.get('anket_done'):
                anket_answer_start(message)
            else:
                message.reply_text(
                    'Добро пожаловать!\
                    \nОсновное меню:',
                    reply_markup=get_main_menu()
                )
    else:
        message.reply_text(
            'Ошибка доступа! Указанный номер не соответсвует UserID.',
            reply_markup=ReplyKeyboardRemove()
        )

def anket_answer_start(message):
    message.reply_text(
        text="Внимание!\
        Все собираемые данные являются анонимными, не подлежат разглашению и будут уничтожены по окончанию Ивента",
    )
    message.reply_text(
        text="Для начала ответьте на несколько вопросов! \nВаш пол:",
        reply_markup=get_anket_gender()
    )

def handle_sticker(update: Update, context: CallbackContext):
    message = update.message
    user = mondb.Valentia22_users.find_one({"user_id": update.effective_message.chat_id})
    if user['status'] == 3:
        context.bot.send_sticker(user['partner'], update.message.sticker.file_id)
    elif user['status'] == 2:
        message.reply_text(
            text="Стикеры будут доступны только после того как оба поделятся сердечками",
        )

def handle_text(update: Update, context: CallbackContext):
    message = update.message
    query = update.callback_query
    user = mondb.Valentia22_users.find_one({"user_id": update.effective_message.chat_id})
    text = update.message.text
    
    #Проверка есть ли Юзер
    if user is None:
        return
    
    #Принятие фотографии
    if user.get('user_photo') is not None and text == REPLY_BACK_MENU_FROM_PHOTO:
        if user.get('user_photo') == "need":
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_photo': "no",
                          }
                 })
            message.reply_text(
                text="❌ Отмена",
                reply_markup=ReplyKeyboardRemove(),
            )
            message.reply_text(
                text="Главное меню:",
                reply_markup=get_main_menu()
            )
    
    heart_list = ["❤️", "<3", "🧡️", "💚️", "💙", "💜", "🖤️", "🤎", "🤍", "💕️", "💞", "💓", "♥️", ":heart:"]
    broken_heart_list = ["💔", "stop", "STOP", "Stop"]

    #Во время общения
    if user['status'] == 2 or user['status'] == 3:
        partn = mondb.Valentia22_users.find_one({"user_id": user['partner']})
        #Дзынь людей
        if text in heart_list and user['status'] == 2:
            if partn.get('like_partner') == 1:
                mondb.Valentia22_users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'like_partner': 1,
                              'status': 3}}
                )
                mondb.Valentia22_users.update_one(
                    {'_id': partn['_id']},
                    {'$set': {'status': 3}}
                )

                dzin_msg_text = "Дзынь! Теперь у вас есть неограниченное количество сообщений, а так же теперь вы можете отправлять стикеры!" 
                message.reply_text(
                    text=dzin_msg_text,
                )

                context.bot.send_message(
                    chat_id=user['partner'],
                    text=dzin_msg_text,
                )

                if user.get('user_photo') is not None:
                    if user.get('user_photo') != "no" and user.get('user_photo') != "need":
                        context.bot.sendPhoto(chat_id=user['partner'],
                                              photo=open(file=user.get('user_photo'), mode='rb'))

                if partn.get('user_photo') is not None:
                    if partn.get('user_photo') != "no" and partn.get('user_photo') != "need":
                        context.bot.sendPhoto(chat_id=partn['partner'],
                                              photo=open(file=partn.get('user_photo'), mode='rb'))
            else:
                mondb.Valentia22_users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'like_partner': 1}}
                )
        #Отключение одного из пары
        elif text in broken_heart_list:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'status': 1,
                          'partner': 0}}
            )
            context.bot.send_message(
                chat_id=user['partner'],
                text=user['user_avatar'] + " покинул комнату...",
                reply_markup=bad_re_search(),
            )

            mondb.Valentia22_users.update_one(
                {'_id': partn['_id']},
                {'$set': {'status': 0,
                          'partner': 0}}
            )
            message.reply_text(
                text="Поиск начался, пожалуйста ожидайте...",
                reply_markup=get_stop_search()
            )
            find_pair = find_pair_in_base(user)
            if find_pair is not None:
                if connect_users(user, find_pair['user_id']):
                    query.edit_message_text(
                        text="Вы были успешно подключены!",
                    )
                    message.reply_text(
                        text="Псс.. не знаешь о чем спросить? Нажми на кнопку! ",
                        reply_markup=get_random_question(),
                    )
                    context.bot.send_sticker(user['chat_id'],
                                             'CAACAgEAAxkBAAICEmAlJqETd9jQMM4j6xYSmVHgzu04AAJ1AAPArAgjbBAAAXUaHGOjHgQ')

                    context.bot.send_message(
                        chat_id=find_pair['user_id'],
                        text="Вы были успешно подключены!",
                    )
                    context.bot.send_message(
                        chat_id=find_pair['user_id'],
                        text="Псс.. не знаешь о чем спросить? Нажми на кнопку! ",
                        reply_markup=get_random_question(),
                    )
                    context.bot.send_sticker(find_pair['user_id'],
                                             'CAACAgEAAxkBAAICEmAlJqETd9jQMM4j6xYSmVHgzu04AAJ1AAPArAgjbBAAAXUaHGOjHgQ')
                    if user['status'] == 2:
                        if user.get('user_photo') is not None:
                            if user.get('user_photo') != "no" and user.get('user_photo') != "need":
                                src = cv2.imread(user.get('user_photo'), cv2.IMREAD_UNCHANGED)
                                gaussian_blur = cv2.GaussianBlur(src, (49, 49), sigmaX=49)
                                # save image
                                status = cv2.imwrite("full_blured_" + user.get('user_photo'), gaussian_blur)
                                print("Image written to file-system : ", status)

                                context.bot.sendPhoto(chat_id=partn.get('user_id'),
                                                    photo=open(file="full_blured_" + user.get('user_photo'), mode='rb'))
                                os.remove("full_blured_" + user.get('user_photo'))

                        if partn.get('user_photo') is not None:
                            if partn.get('user_photo') != "no" and partn.get('user_photo') != "need":
                                src = cv2.imread(partn.get('user_photo'), cv2.IMREAD_UNCHANGED)
                                gaussian_blur = cv2.GaussianBlur(src, (49, 49), sigmaX=49)
                                # save image
                                status = cv2.imwrite("full_blured_" + partn.get('user_photo'), gaussian_blur)
                                print("Image written to file-system : ", status)
                                context.bot.sendPhoto(chat_id=user.get('user_id'),
                                                    photo=open(file="full_blured_" + partn.get('user_photo'), mode='rb'))
                                os.remove("full_blured_" + partn.get('user_photo'))
        #Проверка на лимит сообщении
        elif user['left_message'] > 0 and user['status'] == 2:
            context.bot.send_message(
                chat_id=user['partner'],
                text=user['user_avatar'] + " :  " + text,
            )
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'left_message': user['left_message'] - 1}}
            )
        #Достиг лимита
        elif user['status'] == 2:
            msg_txt = "она" if partn['user_gender'] == 0 else "он"
            message.reply_text(
                text="У вас закончился доступный лимит сообщений! Отправьте ❤️ - если вам понравился этот человек,"
                     "и вы хотели бы продолжить общение. Если " + msg_txt +
                     "тоже отправит сердечко, то вы будете не ограничены в количестве сообщений",
                reply_markup=re_search()
            )
        else:
            context.bot.send_message(
                chat_id=user['partner'],
                text=user['user_avatar'] + ": " + text,
            )
    elif user['status'] == 0 and user.get('user_avatar') is not None:
        if user.get('user_avatar') == "NeedXemo":
            if update.message.text == "🎩 Шляпник" or update.message.text == "🎩😻 Котик в шляпе":
                message.reply_text(
                    'Упс, Нельзя представляться этим именем!'
                )
            else: 
                mondb.Valentia22_users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'user_avatar': update.message.text}}
                )
            mes_text = " "
            if user.get('user_gender') == 0:
                mes_text += "{0}\n".format("Женский")
            elif user.get('user_gender') == 1:
                mes_text += "{0}\n".format("Мужской")
            elif user.get('user_gender') == 2:
                mes_text += "{0}\n".format("Неопределен")
            else:
                message.reply_text(
                    'Ошибка!\n '
                    'Несоответствие данных! Пожалуйста попробуйте еще раз, если ошибка повторится сообщите о ней '
                    '@MON0makh',
                    reply_markup=get_anket_gender()
                )

            mes_text += "Вас интересуют: "
            if user.get('user_partn') == 0:
                mes_text += "{0}\n".format("Парни")
            elif user.get('user_partn') == 1:
                mes_text += "{0}\n".format("Девушки")
            elif user.get('user_partn') == 2:
                mes_text += "{0}\n".format("Оба")
            else:
                message.reply_text(
                    'Ошибка!\n '
                    'Несоответствие данных! Пожалуйста попробуйте еще раз, если ошибка повторится сообщите о ней '
                    '@MON0makh',
                    reply_markup=get_anket_gender()
                )

            mes_text += "Вы на: "
            if user.get('user_course') == 1:
                mes_text += "{}\n".format("1-2 курсе обучения")
            elif user.get('user_course') == 2:
                mes_text += "{}\n".format("3-5 курсе обучения")
            else:
                message.reply_text(
                    'Ошибка!\n '
                    'Несоответстве данных! Пожалуйста попробуйте еще раз, если ошибка повторится сообщите о ней '
                    '@MON0makh',
                    reply_markup=get_anket_gender()
                )
            message.reply_text(
                text="Все готово!\n{0}\nВаш пол: {1}".format(update.effective_message.text, mes_text),
                reply_markup=get_anket_confirm(),
            )

# Telegram inline menu buttons handler
def keyboard_call_handler(update: Update, context: CallbackContext):
    message = update.message
    query = update.callback_query
    data = query.data
    user = mondb.Valentia22_users.find_one({"user_id": update.effective_message.chat_id})

    if data == CALLBACK_ANKET_GIRL or \
            data == CALLBACK_ANKET_BOY or \
            data == CALLBACK_ANKET_ANOTHER:

        if data == CALLBACK_ANKET_GIRL:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_gender': 0}}
            )
        elif data == CALLBACK_ANKET_BOY:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_gender': 1}}
            )

        else:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_gender': 2}}
            )

        query.edit_message_text(
            text="Какой пол вас интересует? ",
            reply_markup=get_anket_partner(),
        )
    elif data == CALLBACK_ANKET_PARTN_GIRL or \
            data == CALLBACK_ANKET_PARTN_BOY or \
            data == CALLBACK_ANKET_PARTN_DOUBLE:

        if data == CALLBACK_ANKET_PARTN_GIRL:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_partn': 0}}
            )
        elif data == CALLBACK_ANKET_PARTN_BOY:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_partn': 1}}
            )

        else:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_partn': 2}}
            )

        query.edit_message_text(
            text="На каком вы курсе обучения? ",
            reply_markup=get_anket_age(),
        )

    elif data == CALLBACK_ANKET_AGE_1 or \
            data == CALLBACK_ANKET_AGE_2:

        if data == CALLBACK_ANKET_AGE_1:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_course': 1}}
            )
        elif data == CALLBACK_ANKET_AGE_2:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'user_course': 2}}
            )

        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'user_avatar': "NeedXemo"}}
        )

        query.edit_message_text(
            text="Почти готово! Теперь отправьте эмоджи который будет являтся вашим аватаром:",
        )
    elif data == CALLBACK_ANKET_CONFIRM:

        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'anket_done': True}}
        )
        query.edit_message_text(
            text="Главное Меню:",
            reply_markup=get_main_menu()
        )
    elif data == CALLBACK_ANKET_DECONF:
        query.edit_message_text(
            text="Ваш пол:",
            reply_markup=get_anket_gender()
        )

    elif data == CALLBACK_OPEN_SEARCH:
        
        msg_txt = ""
        if user['status'] > 1:
            msg_txt = "❗️Внимание❗️ Вы уже находитесь в чате с другим пользователем! Если вы начнете поиск сейчас," \
                      "то вы будете отключены от текущей комнаты! \n\n"

        query.edit_message_text(
            text=msg_txt + "Правила! \nПосле того как вы будете подключены в комнату с другим анонимным пользователем, "
                           "вы можете написать ему анонимно 14 сообщений. Он в свою очередь имеет такое же количество "
                           "сообщений. После того, как вы исчерпаете лимит сообщений, у вас будет возможность "
                           "'оставить сердечко' этому пользователю, и если он тоже оставил сердечко вам, то для вас "
                           "обоих откроются ваши данные, и вы сможете продолжить общение. Вы так же можете "
                           "Поделится своим фото, в начале общения собеседник будет получать сильно размытую версию "
                           "вашей фотографии, "
                           "в случае 'Дзынь' (Оба участника отдали сердечко друг другу), собеседник сможет увидеть "
                           "фото в оригинале.",
            reply_markup=get_start_search(user.get('user_gender'))
        )
    elif data == CALLBACK_START_SEARCH or data == CALLBACK_RE_SEARCH:
        if user['status'] > 1:
            context.bot.send_message(
                chat_id=user['partner'],
                text=user['user_avatar'] + " покинул комнату...",
                reply_markup=bad_re_search(),
            )
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'status': 1,
                          'partner': 0}}
            )
            pair = mondb.Valentia22_users.find_one({"user_id": user['partner']})
            mondb.Valentia22_users.update_one(
                {'_id': pair['_id']},
                {'$set': {'status': 0,
                          'partner': 0}}
            )
        else:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'status': 1}}
            )
        query.edit_message_text(
            text="Поиск начался, пожалуйста ожидайте...",
            reply_markup=get_stop_search()
        )

        find_pair = find_pair_in_base(user)
        if find_pair is not None:
            if connect_users(user, find_pair['user_id']):
                query.edit_message_text(
                    text="Вы были успешно подключены!",
                )
                context.bot.send_message(
                    chat_id=user['user_id'],
                    text="Псс.. не знаешь о чем спросить? Нажми на кнопку! ",
                    reply_markup=get_random_question(),
                )
                context.bot.send_sticker(user['user_id'],
                                         'CAACAgEAAxkBAAICEmAlJqETd9jQMM4j6xYSmVHgzu04AAJ1AAPArAgjbBAAAXUaHGOjHgQ')

                context.bot.send_message(
                    chat_id=find_pair['user_id'],
                    text="Вы были успешно подключены!",
                )
                context.bot.send_message(
                    chat_id=find_pair['user_id'],
                    text="Псс.. не знаешь о чем спросить? Нажми на кнопку! ",
                    reply_markup=get_random_question(),
                )
                context.bot.send_sticker(find_pair['user_id'],
                                         'CAACAgEAAxkBAAICEmAlJqETd9jQMM4j6xYSmVHgzu04AAJ1AAPArAgjbBAAAXUaHGOjHgQ')
                
                if user.get('user_photo') is not None:
                    if user.get('user_photo') != "no" and user.get('user_photo') != "need":
                        src = cv2.imread(user.get('user_photo'), cv2.IMREAD_UNCHANGED)
                        gaussian_blur = cv2.GaussianBlur(src, (49, 49), sigmaX=49)
                        # save image
                        status = cv2.imwrite("full_blured_" + user.get('user_photo'), gaussian_blur)
                        print("Image written to file-system : ", status)

                        context.bot.sendPhoto(chat_id=find_pair.get('user_id'),
                                            photo=open(file="full_blured_" + user.get('user_photo'), mode='rb'))
                        os.remove("full_blured_" + user.get('user_photo'))
                

                if find_pair.get('user_photo') is not None:
                    if find_pair.get('user_photo') != "no" and find_pair.get('user_photo') != "need":
                        src = cv2.imread(find_pair.get('user_photo'), cv2.IMREAD_UNCHANGED)
                        gaussian_blur = cv2.GaussianBlur(src, (49, 49), sigmaX=49)
                        # save image
                        status = cv2.imwrite("full_blured_" + find_pair.get('user_photo'), gaussian_blur)
                        print("Image written to file-system : ", status)
                        context.bot.sendPhoto(chat_id=user.get('user_id'),
                                            photo=open(file="full_blured_" + find_pair.get('user_photo'), mode='rb'))
                        os.remove("full_blured_" + find_pair.get('user_photo'))
    elif data == CALLBACK_STOP_SEARCH:
        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'status': 0}}
        )
        query.edit_message_text(
            text="Правила! \nПосле того как вы будете подключены в комнату с другим анонимным пользователем, "
                 "вы можете написать ему анонимно 14 сообщений. Он в свою очередь имеет такое же количество "
                 "сообщений. После того, как вы исчерпаете лимит сообщений, у вас будет возможность 'оставить "
                 "сердечко' этому пользователю, и если он тоже оставил сердечко вам, то для вас обоих откроются ваши "
                 "данные, и вы сможете продолжить общение. Вы так же можете Поделится своим фото, "
                 "в начале общения собеседник будет получать сильно размытую версию вашей фотографии, "
                 " в случае 'Дзынь' (Оба участника отдали сердечко "
                 "друг другу), собеседник сможет увидеть фото в оригинале.",
            reply_markup=get_start_search(user.get('user_gender'))
        )
    elif data == CALLBACK_BACK_MAIN_MENU:
        query.edit_message_text(
            text="Главное Меню:",
            reply_markup=get_main_menu()
        )
    elif data == CALLBACK_RETURN_TO_MAIN_MENU_FROM_CHAT:
        context.bot.send_message(
            chat_id=user['partner'],
            text=user['user_avatar'] + " покинул комнату...",
            reply_markup=bad_re_search(),
        )
        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'status': 0,
                      'user_partn': 0}}
        )
        pair = mondb.Valentia22_users.find_one({"user_id": user['partner']})
        mondb.Valentia22_users.update_one(
            {'_id': pair['_id']},
            {'$set': {'status': 0,
                      'partner': 0}}
        )
        query.edit_message_text(
            text="Главное Меню:",
            reply_markup=get_main_menu()
        )
    elif data == CALLBACK_RANDOM_QUESTION:
        if user['status'] > 1:
            questions = ["Какой ваш идеальный вечер?", "С чем у вас ассоциируется детство?",
                         "Что бы вы оценили на 10 из 10?", "Аниме?", "Какую музыку предпочитаете?",
                         "Хотели бы вы стать знаменитыми? В какой области?", "Дедлайны горят?"
                                                                             "Любимое место для отдыха в Алмате?",
                         "Где в Алматы лучше всего проводить время?",
                         "Кто ваш любимый препод?", "Есть ли у вас домашнее животное?",
                         "Хотели бы вы жить в другой стране?"
                         "Нааааазад в прошлое! Только что пришли результаты  ЕНТ, твои действия?",
                         "Что вам нравится в вашей специальности?",
                         "Если бы тебе нужно было бы посоветовать фильм человеку, никогда не видевшего кино. Какой бы фильм это был?",
                         "Играете в видеоигры?", "Стипендия на месте?", "Твой совет первашам",
                         "Рахмет или Ракхмет?", "Из какого вы города?",
                         "Какой работой вы бы никогда, не смогли бы заниматся?"
                         "Занимаетесь спортом?", "ЗОЖ или не ЗОЖ?", "Опишите себя за три слова!",
                         "А верите ли вы в любовь с первого взгляда?", "Какие милашки ^^ \nКошки или собачки?",
                         "Ваш любимый вид спорта?",
                         "Уже через пару десятилетий Илан Маск, отправит людей колонизировать Марс! Хотели бы вы, быть первыми колонизатормаи?",
                         "Как вы считеате, любовь существует?",
                         "Что больше всего вам нравилось в школе?", "Что больше всего вам нравится в ВУЗе?",
                         "Какой ваш любимый сериал?", "Какую книгу вы прочли последней?", "Верите ли вы в гороскоп?",
                         "Вы сладкоежки?", "Что лучше? Дарить подарки или Получать подарки... ",
                         "Закончите фразу по своему: мир был бы лучше, если...",
                         "Закончите фразу по совему: Страна была бы лучше, если..."
                         "Закончите фразу по своему: Универ был бы лучше, если...", "Онлайн обучение или Очное?"
                                                                                    "Какой у вас любимый вид искусства?",
                         "Подскажите мне пожалуйстя, как произвести впечатление на человека?", "Какие у вас хобби?",
                         "Кофе или Чай?", "Черный чай или зеленый?", "Что такое счастье?",
                         "Если бы вы могли перевоплотится в животное, то в кто бы это был?",
                         "Квадратный корень из 144", "Ассоциации на букву П...",
                         "Какой ваш любимый Черно-белый фильм?", "Если бы вы были персонажем книги, то какой?"]

            rand_quest = random.randrange(len(questions))
            context.bot.send_message(
                chat_id=user['user_id'],
                text="🎩 Шляпник: " + questions[rand_quest],
            )
            context.bot.send_message(
                chat_id=user['partner'],
                text="🎩 Шляпник: " + questions[rand_quest],
            )
    elif data == CALLBACK_EDIT_MY_DATA:
        if user['status'] > 1:
            mondb.Valentia22_users.update_one(
                {'_id': user['_id']},
                {'$set': {'status': 0,
                          'partner': 0}}
            )
            pair = mondb.Valentia22_users.find_one({"user_id": user['partner']})
            mondb.Valentia22_users.update_one(
                {'_id': pair['_id']},
                {'$set': {'status': 0,
                          'partner': 0}}
            )
            context.bot.send_message(
                chat_id=user['partner'],
                text=user['user_avatar'] + " покинул комнату...",
                reply_markup=bad_re_search(),
            )
        query.edit_message_text(
            text="Ваш пол:",
            reply_markup=get_anket_gender()
        )
    elif data == CALLBACK_CINEMA_NIGHT:
        query.edit_message_text(
            text="14 Февраля в 23:30 на Discord сервере сообщества HUB, пройдет романтическая кинополночь!"
                 " Вход открыт для всех, парой или в одиночку, приходите смотреть кино вместе с нами!",
            reply_markup=get_cinemanight()
        )
    elif data == CALLBACK_ADD_PHOTO:
        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'user_photo': "need",
                      }
             })

        context.bot.send_message(
            chat_id=user['user_id'],
            text="Отлично! Теперь отправьте в чат свое фото. Оно изначально, будет размыто для других,"
                 " они смогут видеть ваше фото в лучшем качестве по ходу общения с вами.",
            reply_markup=REPLY_BACK_TO_MENU_FROM_PHOTO,
        )

def find_pair_in_base(user):
    users = mondb.Valentia22_users.find({'status': 1})

    users_len = users.count()
    print(users_len)

    if users_len <= 1:
        return None

    user_gender = user.get('user_gender')
    user_partn_gender = user.get('user_partn')
    user_course = user.get('user_course')

    must_come_pair = 0
    must_come_pair_data = 0.01

    max_must_come_pair_user = None
    max_must_come_pair_data = 0.01

    best_case = 3.0
    not_best_case = 2.0
    bad_case = 1.0

    # Если пользователь цисгендер и не Другой
    if user_gender == user_partn_gender and user_gender != 2:
        for come_user in users:
            if come_user['_id'] == user['_id']:
                continue
            # Если второй юзер противоположного пола и не другой,
            if user_gender != come_user['user_gender'] and come_user['user_gender'] != 2:
                # Если второй юзер цисгендер
                if come_user['user_gender'] == come_user['user_partn'] and \
                        must_come_pair_data < best_case:
                    must_come_pair = come_user['user_id']
                    must_come_pair_data = best_case

                # если второй юзер би и не другой
                elif come_user['user_partn'] == 2 and come_user['user_gender'] != 2 and \
                        must_come_pair_data < not_best_case:
                    must_come_pair = come_user['user_id']
                    must_come_pair_data = not_best_case
            # корректировки веса
            # если юзеры разных лет, штраф 0.5
            if user_course != come_user['user_course']:
                must_come_pair_data -= 0.5
            # Если юзеры уже переписывались штраф 1.5 за каждую пройденную комнату
            user_chat_hist = user['chat_history'].split()
            if must_come_pair_data > 0:
                for i in range(len(user_chat_hist)):
                    if user_chat_hist[i] == must_come_pair:
                        must_come_pair_data -= 1.5
                    if must_come_pair_data < 0.0:
                        must_come_pair = 0
                        must_come_pair_data = 0.0
                        break
            if must_come_pair_data > max_must_come_pair_data:
                max_must_come_pair_user = come_user
                max_must_come_pair_data = must_come_pair_data
    # Если пользователь гомосексуал
    elif user_partn_gender != user_gender and user_gender != 2:
        for come_user in users:
            if come_user['_id'] == user['_id']:
                continue
            # Если второй юзер того же пола и той же ориентации т.е. гомо
            if come_user['user_gender'] == user_gender and come_user['user_partn'] == user_partn_gender and \
                    must_come_pair_data < best_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = best_case
            elif come_user['user_gender'] == user_gender and come_user['user_partn'] == 2 and \
                    must_come_pair_data < not_best_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = not_best_case
            # Если второй пользователь другой и би или ищет пол юзера
            elif come_user['user_gender'] == 2 and come_user['user_partn'] == 2 or \
                    (come_user['user_partn'] != 2 and come_user['user_partn'] != user_gender) and \
                    must_come_pair_data < bad_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = bad_case

            # Корректировки веса
            if user_course != come_user['user_course']:
                must_come_pair_data -= 0.5
                # Если юзеры уже переписывались штраф 1.5 за каждую пройденную комнату
            user_chat_hist = user['chat_history'].split()
            if must_come_pair_data > 0:
                for i in range(len(user_chat_hist)):
                    if user_chat_hist[i] == must_come_pair:
                        must_come_pair_data -= 1.5
                    if must_come_pair_data < 0.0:
                        must_come_pair = 0
                        must_come_pair_data = 0.0
                        break
            if must_come_pair_data > max_must_come_pair_data:
                max_must_come_pair_user = come_user
                max_must_come_pair_data = must_come_pair_data
    # Если пользователь би и не другой
    elif user_partn_gender == 2 and user_gender != 2:
        for come_user in users:
            if come_user['_id'] == user['_id']:
                continue
            # Если второй юзер тоже би
            if come_user['user_partn'] == 2 and \
                    must_come_pair_data < best_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = best_case
            # Если второй юзер противоположного пола или того же пола но гомо
            elif come_user['user_gender'] != user_gender or \
                    (come_user['user_gender'] == user_gender and come_user['user_partn'] != come_user[
                        'user_gender']) and \
                    must_come_pair_data < not_best_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = not_best_case

            if user_course != come_user['user_course']:
                must_come_pair_data -= 0.5
            # Если юзеры уже переписывались штраф 1.5 за каждую пройденную комнату
            user_chat_hist = user['chat_history'].split()
            if must_come_pair_data > 0:
                for i in range(len(user_chat_hist)):
                    if user_chat_hist[i] == must_come_pair:
                        must_come_pair_data -= 1.5
                    if must_come_pair_data < 0.0:
                        must_come_pair = 0
                        must_come_pair_data = 0.0
                        break
            if must_come_pair_data > max_must_come_pair_data:
                max_must_come_pair_user = come_user
                max_must_come_pair_data = must_come_pair_data
    # Если другой
    elif user_gender == 2:
        for come_user in users:
            if come_user['_id'] == user['_id']:
                continue
            # Если оба другие
            if come_user['user_gender'] == 2 and must_come_pair_data < best_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = best_case
            # Если второй юзер не своей ориентации
            elif come_user['user_partn'] != come_user['user_gender'] and must_come_pair_data < not_best_case:
                must_come_pair = come_user['user_id']
                must_come_pair_data = not_best_case

            if user_course != come_user['user_course']:
                must_come_pair_data -= 0.5
            # Если юзеры уже переписывались штраф 1.5 за каждую пройденную комнату
            user_chat_hist = user['chat_history'].split()
            if must_come_pair_data > 0:
                for i in range(len(user_chat_hist)):
                    if user_chat_hist[i] == must_come_pair:
                        must_come_pair_data -= 1.5
                    if must_come_pair_data < 0.0:
                        must_come_pair = 0
                        must_come_pair_data = 0.0
                        break
            if must_come_pair_data > max_must_come_pair_data:
                max_must_come_pair_user = come_user
                max_must_come_pair_data = must_come_pair_data
    return max_must_come_pair_user

def connect_users(user, pair_id):
    if len(user['chat_history'].split())<5:
        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'status': 2,
                      'left_message': 14,
                      'partner': pair_id,
                      'like_partner': 0,
                      'chat_history': user['chat_history'] + " " + str(pair_id)}
            })
        pair = mondb.Valentia22_users.find_one({"user_id": pair_id})
        mondb.Valentia22_users.update_one(
            {'_id': pair['_id']},
            {'$set': {'status': 2,
                      'left_message': 14,
                      'like_partner': 0,
                      'partner': user['user_id'],
                      'chat_history': pair['chat_history'] + " " + str(user['user_id'])}}
        )
    else:
        mylist = user['chat_history'].split()
        del mylist[0]
        mystr = " "
        mystr = mystr.join(mylist)
        mondb.Valentia22_users.update_one(
            {'_id': user['_id']},
            {'$set': {'status': 2,
                      'left_message': 14,
                      'partner': pair_id,
                      'like_partner': 0,
                      'chat_history': mystr + " " + str(pair_id)}
             })
        pair = mondb.Valentia22_users.find_one({"user_id": pair_id})
        mondb.Valentia22_users.update_one(
            {'_id': pair['_id']},
            {'$set': {'status': 2,
                      'left_message': 14,
                      'like_partner': 0,
                      'partner': user['user_id'],
                      'chat_history': mystr + " " + str(user['user_id'])}}
        )
    return True

def main():
    updater = Updater(
        token=TG_TOKEN,
        use_context=True,
    )

    logging.info("Altair8 started")
    # Commands handler add, IF you u need add new command use it
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', on_start))
    # dp.add_handler(CommandHandler('research', comm_research))
    dp.add_handler(CommandHandler('advert', comm_advert))
    dp.add_handler(CallbackQueryHandler(callback=keyboard_call_handler, pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.sticker, handle_sticker))
    dp.add_handler(MessageHandler(Filters.contact, on_contact))
    dp.add_handler(MessageHandler(Filters.photo, get_photo))
    dp.add_handler(MessageHandler(Filters.text, handle_text))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
