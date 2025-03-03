from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

# Замените на ваш Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Получаем данные от Alertmanager
    data = request.json
    print("Received alert:", data)

    # Формируем сообщение для Telegram
    message = ""
    for alert in data.get('alerts', []):
        status = alert.get('status', 'unknown')
        summary = alert.get('annotations', {}).get('summary', 'No summary')
        description = alert.get('annotations', {}).get('description', 'No description')
        instance = alert.get('labels', {}).get('instance', 'No instance')

        message += f"Status: {status}\n"
        message += f"Instance: {instance}\n"
        message += f"Summary: {summary}\n"
        message += f"Description: {description}\n\n"

    # Отправляем сообщение в Telegram
    if message:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'  # Можно использовать HTML для форматирования
        }
        response = requests.post(TELEGRAM_API_URL, json=payload)
        if response.status_code != 200:
            return jsonify({"error": "Failed to send message to Telegram"}), 500

    return jsonify({"status": "ok"}), 200
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     # Получаем данные от Alertmanager
#     data = request.json
#     print("Received alert:", data)

#     # Формируем сообщение для Telegram
#     message_parts = []
#     for alert in data.get('alerts', []):
#         status = alert.get('status', 'unknown')
#         summary = alert.get('annotations', {}).get('summary', 'No summary')
#         description = alert.get('annotations', {}).get('description', 'No description')
#         instance = alert.get('labels', {}).get('instance', 'No instance')

#         # Создаем форматированный блок для каждого алерта
#         message_part = (
#             f"*Status:* `{status}`\n"
#             f"*Instance:* `{instance}`\n"
#             f"*Summary:* {summary}\n"
#             f"*Description:* {description}\n\n"
#         )
#         message_parts.append(message_part)

#     # Объединяем все части сообщений
#     message = "".join(message_parts)

#     # Отправляем сообщение в Telegram
#     if message:
#         payload = {
#             'chat_id': TELEGRAM_CHAT_ID,
#             'text': message,
#             'parse_mode': 'Markdown'  # Используем Markdown для форматирования
#         }
#         response = requests.post(TELEGRAM_API_URL, json=payload)
#         if response.status_code != 200:
#             return jsonify({"error": "Failed to send message to Telegram"}), 500

#     return jsonify({"status": "ok"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)