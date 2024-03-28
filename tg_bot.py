import json
import os
import subprocess
import time

import telebot

from keyboard import back_keyboard, delete_keyboard, main_keyboard

global ADMIN_ID
global DELETE_ID
DELETE_ID = 0

from dotenv import load_dotenv

# Load variables from .env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Tg tokens
ADMIN_ID = json.loads(os.getenv("ADMIN_ID"))
ADMIN_ID = {int(key): value for key, value in ADMIN_ID.items()}
BOT_TOKEN = os.getenv("TOKEN")
VPN_FOLDER = os.getenv("VPN_FOLDER")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "🧾Hello! Here you can create new VPN protocols or delete existing ones",
        reply_markup=main_keyboard(),
    )


@bot.message_handler(content_types="text")  # Bot work
def main(message):
    if message.text == "✅Create VPN" and message.chat.id in ADMIN_ID.keys():
        bot.send_message(
            message.chat.id,
            "Enter VPN protocol name",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, create_vpn)
    elif message.text == "📛Remove VPN" and message.chat.id in ADMIN_ID.keys():
        list_vpns = get_current_vpn()

        bot.send_message(
            message.chat.id,
            f"Enter the protocol number\nto be <b>DELETED</b>:\n{list_vpns}",
            reply_markup=back_keyboard(),
            parse_mode="html",
        )
        bot.register_next_step_handler(message, delete_protocol)
    elif message.text == "📝Get VPN" and message.chat.id in ADMIN_ID.keys():
        list_vpns = get_current_vpn()

        bot.send_message(
            message.chat.id,
            f"Enter the protocol number\nyou want to receive:\n{list_vpns}",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, get_protocol)
    else:
        come_back(message=message, message_text="🚫Access denied")


def create_vpn(message):
    if message.text == "Back":
        come_back(message=message)
    else:
        if message.text:
            try:
                file_name = message.text
                # Запуск процесса создания VPN
                process = subprocess.Popen(
                    ["bash", f"{VPN_FOLDER}/openvpn-install.sh"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                skip_menu(last_string="exit", process=process)
                # First command
                process.stdin.write("1\n".encode())
                process.stdin.flush()
                skip_menu(last_string="for the client", process=process)
                # Second command
                process.stdin.write(f"{file_name}\n".encode())
                process.stdin.flush()

                # Close process
                process.stdin.close()

                bot.send_message(message.chat.id, "⌛File incoming, wait")

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
                come_back(message=message, message_text=f"Возникла проблема при создании файла: {str(e)}")
        else:
            come_back(message=message, message_text="Invalid command")


def delete_protocol(message):
    if message.text == "Back":
        come_back(message=message)
    else:
        if message.text:
            dict_vpns = get_dict_vpns()
            if str(message.text) not in dict_vpns.keys():
                come_back(
                    message=message,
                    message_text=f"This number: {message.text} is not available,\nTotal {len(dict_vpns)} VPN files",
                )
            else:
                global DELETE_ID
                DELETE_ID = message.text
                bot.send_message(
                    message.chat.id,
                    f"Are you sure you want to delete {dict_vpns[message.text]}?",
                    reply_markup=delete_keyboard(),
                )
                bot.register_next_step_handler(message, remove_protocol)
        else:
            come_back(message=message, message_text="Invalid command")


def remove_protocol(message):
    if message.text == "Back":
        list_vpns = get_current_vpn()

        bot.send_message(
            message.chat.id,
            f"Enter the protocol number\to be deleted:\n{list_vpns}",
            reply_markup=back_keyboard(),
        )
        bot.register_next_step_handler(message, delete_protocol)
    else:
        if message.text:
            answer = message.text
            if answer in ("Main menu", "✅Don't delete"):
                come_back(message=message)
            elif answer == "💀Delete":
                dict_vpns = get_dict_vpns()
                process = subprocess.Popen(
                    ["bash", f"{VPN_FOLDER}/openvpn-install.sh"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                skip_menu(last_string="exit", process=process)
                # First command
                process.stdin.write("2\n".encode())
                process.stdin.flush()

                skip_menu(last_string=f"{max(dict_vpns.keys())})", process=process)

                # Second command
                process.stdin.write(f"{str(DELETE_ID)}\n".encode())
                process.stdin.flush()

                process.stdin.write(f"y\n".encode())
                process.stdin.flush()
                # Close process
                process.stdin.close()

                os.remove(f"/root/{dict_vpns[DELETE_ID]}.ovpn")
                come_back(message=message, message_text="Protocol deleted.\nSelect a category:")
        else:
            come_back(message=message, message_text="Invalid command")


def get_protocol(message):
    if message.text == "Back":
        come_back(message=message)
    else:
        if message.text:
            dict_vpns = get_dict_vpns()
            if str(message.text) not in dict_vpns.keys():
                come_back(
                    message=message,
                    message_text=f"There isn't given number: {message.text},\nTotal {len(dict_vpns)} VPN files",
                )

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
            come_back(message=message, message_text="Invalid command")


def skip_menu(last_string: str, process: subprocess.Popen) -> None:
    while True:
        if last_string in process.stdout.readline().decode().lower():
            break


def come_back(message, message_text: str = "Select a category: ") -> None:
    bot.send_message(
        message.chat.id,
        message_text,
        reply_markup=main_keyboard(),
    )
    bot.register_next_step_handler(message, main)


def get_current_vpn() -> str:
    with open("/etc/openvpn/server/easy-rsa/pki/index.txt", "r") as f:
        vpns = f.read()
    list_vpn = [i.split("=")[1] for i in vpns.split("\n")[1:] if i.startswith("V")]
    enumerate_list = [f"{i}) {list_vpn[i-1]}" for i in range(1, len(list_vpn) + 1)]
    return "\n".join(enumerate_list)


def get_dict_vpns() -> dict:
    list_vpn = get_current_vpn()
    return {i.split(" ")[0][:-1]: i.split(" ")[1] for i in list_vpn.split("\n")}


if __name__ == "__main__":
    bot.polling(none_stop=True)
