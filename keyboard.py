from telebot import types

def main_keyboard():
    markup_main = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    button1 = "✅Create VPN"
    button2 = "📛Remove VPN"
    button3 = "📝Get VPN"
    markup_main.row(button1)
    markup_main.row(button2)
    markup_main.row(button3)
    return markup_main

def delete_keyboard():
    markup_delete = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = "💀Delete"
    button2 = "✅Don't delete"
    button3 = "Back"
    button4 = "Main menu"
    markup_delete.row(button1, button2)
    markup_delete.row(button3)
    markup_delete.row(button4)
    return markup_delete 

def back_keyboard():
    markup_back = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = "Back"
    markup_back.row(button1)
    return markup_back