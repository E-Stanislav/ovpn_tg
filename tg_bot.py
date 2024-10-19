import json
import os
import subprocess
import time

import psutil
import telebot
from dotenv import load_dotenv

from keyboard import back_keyboard, delete_keyboard, main_keyboard

# Load environment variables
load_dotenv()

# Bot and Admin details
ADMIN_ID = {int(key): value for key, value in json.loads(os.getenv("ADMIN_ID")).items()}
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
    elif message.text == "💻System info" and message.chat.id in ADMIN_ID.keys():
        bot.send_message(message.chat.id, "⌛Collecting system info...")
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1, percpu=True)
        disk = psutil.disk_usage(psutil.disk_partitions()[0].mountpoint)

        summary = (
            f"🧠 RAM: {mem.used / (1024 ** 3):.2f}/{mem.total / (1024 ** 3):.2f} GB\n"
            f"🖥️ CPU: {cpu[0]}%\n"
            f"💽 Disk: {disk.used / (1024 ** 3):.2f}/{disk.total / (1024 ** 3):.2f} GB ({disk.percent}%)"
        )
        come_back(message, summary)
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
                come_back(message=message, message_text=f"There was a problem creating the file: {str(e)}")
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
        return come_back(message)

    dict_vpns = get_dict_vpns()
    vpn_file = dict_vpns.get(message.text)

    if vpn_file:
        with open(f"/root/{vpn_file}.ovpn", "rb") as caps:
            bot.send_document(message.chat.id, document=caps, reply_markup=main_keyboard())
        bot.register_next_step_handler(message, main)
    else:
        come_back(message, f"There isn't a file for number: {message.text},\nTotal {len(dict_vpns)} VPN files")


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
