import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Список пользователей', callback_data='get_users')
    keyboard.add(button)
    bot.send_message(message.chat.id, 'Нажми кнопку для получения списка пользователей.', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'get_users':
        try:
            response = requests.get('http://localhost:8000/users')
            users = response.json()
            keyboard = InlineKeyboardMarkup(row_width=1)
            for user in users:
                button = InlineKeyboardButton(user['name'], callback_data=f'user_{user["id"]}')
                keyboard.add(button)
            bot.send_message(call.message.chat.id, 'Список пользователей:', reply_markup=keyboard)
        except:
            bot.send_message(call.message.chat.id, 'Ошибка при получении списка.')
    
    elif call.data.startswith('user_'):
        user_id = int(call.data.split('_')[1])
        keyboard = InlineKeyboardMarkup(row_width=1)
        ban_button = InlineKeyboardButton('Заблокировать', callback_data=f'action_ban_{user_id}')
        kick_button = InlineKeyboardButton('Кикнуть', callback_data=f'action_kick_{user_id}')
        ping_button = InlineKeyboardButton('Пингануть', callback_data=f'action_ping_{user_id}')
        keyboard.add(ban_button, kick_button, ping_button)
        bot.send_message(call.message.chat.id, 'Выберите действие для пользователя:', reply_markup=keyboard)
    
    elif call.data.startswith('action_'):
        parts = call.data.split('_')
        action = parts[1]
        user_id = int(parts[2])
        try:
            response = requests.post('http://localhost:8000/action', json={'user_id': user_id, 'action': action})
            result = response.json()
            if 'success' in result:
                bot.send_message(call.message.chat.id, f'Действие выполнено: {result["success"]}')
            else:
                bot.send_message(call.message.chat.id, f'Ошибка: {result.get("error")}')
        except:
            bot.send_message(call.message.chat.id, 'Ошибка при выполнении действия.')

bot.polling()