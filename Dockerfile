# Базовый образ
FROM python:3.9-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY telegram_bot.py .

# Открытие порта
EXPOSE 5000

# Команда для запуска приложения
CMD ["python", "telegram_bot.py"]