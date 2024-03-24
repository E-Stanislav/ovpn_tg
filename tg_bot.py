import telebot
from keyboard import (
    main_keyboard,
    back_keyboard,
    delete_keyboard,
)
import json
import time
import subprocess
from telebot.types import InputMediaPhoto
import os
from telebot import types

global ADMIN_ID
global DELETE_ID
# ADMIN_ID = {528596693: "ef_stas"}  # ID админа
DELETE_ID = 0

# bot = telebot.AsyncTeleBot(token)
from dotenv import load_dotenv
from telebot import TeleBot

# Загружаем переменные из .env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Токен бота
ADMIN_ID = json.loads(os.getenv("ADMIN_ID"))
ADMIN_ID = {int(key):value for key, value in ADMIN_ID.items()}
BOT_TOKEN = os.getenv("TOKEN")

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "🧾Привет! Здесь ты можешь создать новые протоколы VPN или удалить существующие",
        reply_markup=main_keyboard(),
    )


@bot.message_handler(content_types="text")  # Работа бота
def main(message):
    if message.text == "✅Создать VPN" and message.chat.id in ADMIN_ID.keys():
        bot.send_message(
            message.chat.id,
            "Введи название файла",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, create_vpn)
    elif message.text == "📛Удалить VPN" and message.chat.id in ADMIN_ID.keys():
        list_vpns = get_current_vpn()

        bot.send_message(
            message.chat.id,
            f"Введи номер протокола,\nкоторый надо удалить:\n{list_vpns}",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, delete_protocol)
    elif message.text == "📝Получить VPN" and message.chat.id in ADMIN_ID.keys():
        list_vpns = get_current_vpn()

        bot.send_message(
            message.chat.id,
            f"Введи номер протокола,\nкоторый хотите получить:\n{list_vpns}",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, get_protocol)
    else:
        bot.send_message(message.chat.id, "Нет доступа", reply_markup=main_keyboard())
        bot.register_next_step_handler(message, main)


def create_vpn(message):
    if message.text == "Назад":
        bot.send_message(
            message.chat.id,
            "Выберите категорию: ",
            reply_markup=main_keyboard(),
        )
        bot.register_next_step_handler(message, main)
    else:
        if message.text:
            try:
                file_name = message.text
                # Запуск процесса создания VPN
                process = subprocess.Popen(
                    ["bash", "/root/openvpn-install/openvpn-install.sh"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                skip_menu(last_string="exit", process=process)
                # Первая команда
                process.stdin.write("1\n".encode())
                process.stdin.flush()
                skip_menu(last_string="for the client", process=process)
                # Вторая команда
                process.stdin.write(f"{file_name}\n".encode())
                process.stdin.flush()

                # Закрытие потока ввода
                process.stdin.close()

                bot.send_message(message.chat.id, "⌛File incoming")

                while True:  # Необходимо пару секунд на создание файлов
                    if f"{file_name}.ovpn" in os.listdir("/root/"):
                        break
                    else:
                        time.sleep(5)

                with open(rf"/root/{file_name}.ovpn", "rb") as caps:
                    caps.seek(0)
                    bot.send_document(
                        message.chat.id,
                        document=caps,
                        reply_markup=main_keyboard(),
                    )

                bot.register_next_step_handler(message, main)
            except Exception as e:
                bot.send_document(
                    message.chat.id,
                    f"Возникла проблема при создании файла: {e}",
                    reply_markup=main_keyboard(),
                )
                bot.register_next_step_handler(message, main)
        else:
            bot.send_message(message.chat.id, "Неверная команда", reply_markup=main_keyboard())
            bot.register_next_step_handler(message, main)


def delete_protocol(message):
    if message.text == "Назад":
        bot.send_message(
            message.chat.id,
            "Выберите категорию: ",
            reply_markup=main_keyboard(),
        )
        bot.register_next_step_handler(message, main)
    else:
        if message.text:
            dict_vpns = get_dict_vpns()
            if str(message.text) not in dict_vpns.keys():
                bot.send_message(
                    message.chat.id,
                    f"Данного номера: {message.text} нет,\nВсего {len(dict_vpns)} VPN файлов",
                    reply_markup=main_keyboard(),
                )
                bot.register_next_step_handler(message, main)
            else:
                global DELETE_ID
                DELETE_ID = message.text
                bot.send_message(
                    message.chat.id,
                    f"Уверены, что хотите удалить {dict_vpns[message.text]}?",
                    reply_markup=delete_keyboard(),
                )
                bot.register_next_step_handler(message, remove_protocol)
        else:
            bot.send_message(message.chat.id, "Неверная команда", reply_markup=main_keyboard())
            bot.register_next_step_handler(message, main)


def remove_protocol(message):
    if message.text == "Назад":
        list_vpns = get_current_vpn()

        bot.send_message(
            message.chat.id,
            f"Введи номер протокола,\nкоторый надо удалить:\n{list_vpns}",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, delete_protocol)
    else:
        if message.text:
            answer = message.text
            if answer in ("Главное меню", "✅Не удалять"):
                bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=main_keyboard())
                bot.register_next_step_handler(message, main)
            elif answer == "💀Удалить":
                dict_vpns = get_dict_vpns()
                process = subprocess.Popen(
                    ["bash", "/root/openvpn-install/openvpn-install.sh"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                skip_menu(last_string="exit", process=process)
                # Первая команда
                process.stdin.write("2\n".encode())
                process.stdin.flush()
                # 1/0
                skip_menu(last_string=f"{max(dict_vpns.keys())})", process=process)

                # Вторая команда
                process.stdin.write(f"{str(DELETE_ID)}\n".encode())
                process.stdin.flush()

                process.stdin.write(f"y\n".encode())
                process.stdin.flush()
                # Закрытие потока ввода
                process.stdin.close()

                os.remove(f"/root/{dict_vpns[DELETE_ID]}.ovpn")

                bot.send_message(message.chat.id, "Протокол удален.\nВыберите категорию:", reply_markup=main_keyboard())
                bot.register_next_step_handler(message, main)
        else:
            bot.send_message(message.chat.id, "Неверная команда", reply_markup=main_keyboard())
            bot.register_next_step_handler(message, main)


def get_protocol(message):
    if message.text == "Назад":
        bot.send_message(
            message.chat.id,
            "Выберите категорию: ",
            reply_markup=main_keyboard(),
        )
        bot.register_next_step_handler(message, main)
    else:
        if message.text:
            dict_vpns = get_dict_vpns()
            if str(message.text) not in dict_vpns.keys():
                bot.send_message(
                    message.chat.id,
                    f"Данного номера: {message.text} нет,\nВсего {len(dict_vpns)} VPN файлов",
                    reply_markup=main_keyboard(),
                )
                bot.register_next_step_handler(message, main)
            else:
                with open(rf"/root/{dict_vpns[message.text]}.ovpn", "rb") as caps:
                    caps.seek(0)
                    bot.send_document(
                        message.chat.id,
                        document=caps,
                        reply_markup=main_keyboard(),
                    )

                bot.register_next_step_handler(message, main)
        else:
            bot.send_message(message.chat.id, "Неверная команда", reply_markup=main_keyboard())
            bot.register_next_step_handler(message, main)


def skip_menu(last_string: str, process: subprocess.Popen) -> None:
    while True:
        if last_string in process.stdout.readline().decode().lower():
            break


def get_current_vpn():
    with open("/etc/openvpn/server/easy-rsa/pki/index.txt", "r") as f:
        vpns = f.read()
    list_vpn = [i.split("=")[1] for i in vpns.split("\n")[1:] if i.startswith("V")]
    enumerate_list = [f"{i}) {list_vpn[i-1]}" for i in range(1, len(list_vpn) + 1)]
    return "\n".join(enumerate_list)


def get_dict_vpns():
    list_vpn = get_current_vpn()
    return {i.split(" ")[0][:-1]: i.split(" ")[1] for i in list_vpn.split("\n")}


if __name__ == "__main__":
    bot.polling(none_stop=True)
