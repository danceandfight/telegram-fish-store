import os
import logging
import redis

from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultDocument
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from elasticpath_requests import (get_products_names_ids, get_products_prices, 
    get_product_by_id,get_elasticpath_token, add_product_to_cart, get_formatted_cart_content, 
    get_cart_item_names_and_ids, remove_cart_item, save_client)

_database = None


def start(bot, update):
    reply_markup = make_keyboard(names_and_ids)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "HANDLE_MENU"


def make_keyboard(names_and_ids):
    keyboard = [[InlineKeyboardButton(str(name), callback_data=str(prod_id))] for name, prod_id in names_and_ids]
    keyboard.append([InlineKeyboardButton('View cart', callback_data='cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def handle_menu(bot, update):
    query = update.callback_query
    if query.data == 'cart':
        reply_markup, message = get_cart_message(ep_token, query.message.chat_id)
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
        return "HANDLE_CART"
    product_name, product_description, amount_in_stock, price, image_link = get_product_by_id(ep_token, query.data, prices)
    
    caption = f"{product_name}\n{product_description}\nIn stock: {amount_in_stock} kgs\n{price}$ per kg\n"
    keyboard = [
        [InlineKeyboardButton('Back to menu', callback_data='menu')], 
        [InlineKeyboardButton('Add 1 kg', callback_data=f'1/{query.data}'),
        InlineKeyboardButton('Add 5 kg', callback_data=f'5/{query.data}'),
        InlineKeyboardButton('Add 10 kg', callback_data=f'10/{query.data}')],
        [InlineKeyboardButton('Cart', callback_data='cart')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_photo(chat_id=query.message.chat_id, photo=image_link, caption=caption, reply_markup=reply_markup)
    
    bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        )
    return "HANDLE_DESCRIPTION"


def get_cart_message(token, user_id):
    message = get_formatted_cart_content(ep_token, user_id)
    cart_item_ids = get_cart_item_names_and_ids(ep_token, user_id)
    keyboard = [[InlineKeyboardButton(f'Remove {item_name}', callback_data=str(item_id))] for item_id, item_name in cart_item_ids]
    keyboard += [[InlineKeyboardButton('Back to menu', callback_data='menu')]]
    keyboard += [[InlineKeyboardButton('Finish order', callback_data='waiting_email')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup, message


def handle_description(bot, update):
    query = update.callback_query
    if query.data == 'menu':
        reply_markup = make_keyboard(names_and_ids)
        update.callback_query.message.reply_text('Please choose:', reply_markup=reply_markup)
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
        return "HANDLE_MENU"
    elif query.data == 'cart':
        reply_markup, message = get_cart_message(ep_token, query.message.chat_id)
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
        return "HANDLE_CART"
    else:
        quantity, prod_id = query.data.split('/')
        print(query.message.chat_id)
        add_product_to_cart(ep_token, query.message.chat_id, prod_id, int(quantity))
        return "HANDLE_DESCRIPTION"


def handle_cart(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    if query.data == 'menu':
        reply_markup = make_keyboard(names_and_ids)
        update.callback_query.message.reply_text('Please choose:', reply_markup=reply_markup)
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
        return 'HANDLE_MENU'
    if query.data == 'waiting_email':
        bot.send_message(chat_id=query.message.chat_id, text='Enter your e-mail')
        return 'WAITING_EMAIL'
    else:
        remove_cart_item(ep_token, query.message.chat_id, query.data)
        reply_markup, message = get_cart_message(ep_token, query.message.chat_id)
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
        return "HANDLE_CART"   


def handle_email(bot, update):
    chat_id = update.message.chat_id
    email = update.message.text
    update.message.reply_text(f'You submitted {email}')
    save_client(ep_token, chat_id, email)


def handle_users_reply(bot, update):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")
    
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': handle_email,
        }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)

def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        database_password = os.getenv("REDIS_PASSWORD")
        database_host = os.getenv("REDIS_HOST")
        database_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    load_dotenv()
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    ep_token = get_elasticpath_token(client_id, client_secret)
    prices = get_products_prices(ep_token)
    names_and_ids = get_products_names_ids(ep_token)

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
