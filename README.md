# Telegram Bot для оповещений через Webhook

Этот проект представляет собой Telegram-бота, который получает уведомления от Alertmanager через вебхук и отправляет их в указанный Telegram-чат. Бот работает внутри Docker-контейнера и использует Flask для обработки HTTP-запросов.

## Структура проекта

- `Dockerfile` - файл для сборки Docker-образа.
- `docker-compose.yml` - конфигурация для запуска контейнера с ботом.
- `telegram_bot.py` - основной скрипт бота, который обрабатывает вебхуки и отправляет сообщения в Telegram.
- `requirements.txt` - список зависимостей Python.


**Собераем и запускаем Docker-образ**:

```
docker-compose build
docker-compose up -d
docker logs -f telegram-bot-alert
```

## Конфигурация Docker Compose

```
services:
  telegram-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: telegram-bot-alert
    ports:
      - "35111:5000"  # Проброс порта 5000 контейнера на порт 35111 хоста
    restart: always
    environment:
      - TELEGRAM_BOT_TOKEN=${TOKEN}
      - TELEGRAM_CHAT_ID=${CHAT_ID}
    networks:
      - monitoring-network

networks:
  monitoring-network:
    name: monitoring-network
    external: true
```

##  `telegram_bot.py`

```
from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Изменение правил и получение доменного имени

Необходимо изменить alertmanager.yml на отправку уведомлений в webhook
```
route:
  receiver: 'telegram-webhook'

receivers:
  - name: 'telegram-webhook'
    webhook_configs:
      - url: 'http://skayfaks.keenetic.pro:35111/webhook'
        send_resolved: true
```

## Для работы webhook необходимо доменное имя и ssl сертификат (допишу позже)

проверка webhook

```
curl -X POST https://api.telegram.org/bot<ТОКЕН>/setWebhook?url=https://wh1t.skayfaks.keenetic.pro/webhook
```
![image](https://github.com/user-attachments/assets/534e1d33-fc48-4664-a49b-85b148f06b3e)


```
curl https://api.telegram.org/bot<ТОКЕН>/getWebhookInfo
```
![image](https://github.com/user-attachments/assets/8029ba1a-2563-4a5a-a3de-fab929372be3)


## Проверка, отправка тестового test_payload.json
```
curl -X POST http://skayfaks.keenetic.pro:35111/webhook      -H "Content-Type: application/json"      -d @test_payload.json
```

![image](https://github.com/user-attachments/assets/e9108dea-5a08-43e9-ba23-442edc7189c4)
