# Managing OpenVpn protocols via TG
Телеграмм бот для управления OpenVPN протоколами <br>
Создание/Удаление/Получение текущих<br>
### Установка зависимостей и запуск:
```bash
apt update
apt install python3-pip
pip3 install -r requirements.txt
python3 tg_bot.py
```
Для работы бота необходимо создать файл `.env`,<br>
Который включает содержит ключ `TOKEN`, c токеном вашего бота.<br>
А так же `ADMIN_ID`, имеющий структуру `{"544496693": "your_name"}`<br>