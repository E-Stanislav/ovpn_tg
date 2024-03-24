import json
from telebot import types

def main_keyboard():
    markup_main = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    button1 = "✅Создать VPN"
    button2 = "📛Удалить VPN"
    button3 = "📝Получить VPN"
    markup_main.row(button1)
    markup_main.row(button2)
    markup_main.row(button3)
    return markup_main

def delete_keyboard():
    markup_qiwi_back = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = "💀Удалить"
    button2 = "✅Не удалять"
    button3 = "Назад"
    button4 = "Главное меню"
    markup_qiwi_back.row(button1, button2)
    markup_qiwi_back.row(button3)
    markup_qiwi_back.row(button4)
    return markup_qiwi_back 

def back_keyboard():
    markup_qiwi_back = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = "Назад"
    markup_qiwi_back.row(button1)
    return markup_qiwi_back