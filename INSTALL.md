# Инструкция по установке и запуску проекта

## Требования к Python

**Важно**: Проект требует Python 3.11 или Python 3.12.  
Python 3.13+ не поддерживается из-за отсутствия готовых пакетов для некоторых зависимостей.

### Установка правильной версии Python

1. Скачайте Python 3.12 с https://www.python.org/downloads/
2. При установке отметьте галочку "Add Python to PATH"
3. Проверьте версию:
   ```bash
   python --version  # Должно быть Python 3.11.x или 3.12.x
   ```

## Установка зависимостей

### Вариант 1: Локальная разработка (рекомендуется)

```bash
# Перейдите в директорию backend
cd backend

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env (скопируйте из .env.example)
copy .env.example .env

# Отредактируйте .env при необходимости
# Минимальная конфигурация уже настроена для локальной разработки
```

### Вариант 2: Docker (рекомендуется для продакшена)

```bash
# Убедитесь что Docker Desktop запущен
cd backend

# Запустите все сервисы
docker-compose up -d

# Проверьте логи
docker-compose logs -f backend
```

## Запуск приложения

### Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступно по адресу: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Приложение будет доступно по адресу: http://localhost:5173

## Проверка работы

1. Откройте http://localhost:8000/docs
2. Проверьте endpoint `/api/search?q=test`
3. Должны вернуться результаты поиска с треками

## Настройка VK API (опционально)

Для работы с VK Music API:

1. Создайте приложение в VK Developers: https://dev.vk.com/
2. Выберите тип приложения "Standalone"
3. Получите `client_id` и `client_secret`
4. Добавьте в `.env`:
   ```
   VK_CLIENT_ID=ваш_client_id
   VK_CLIENT_SECRET=ваш_client_secret
   ```

## Настройка Telegram Bot

1. Создайте бота через @BotFather в Telegram
2. Получите токен
3. Добавьте в `.env`:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен
   ```

## Troubleshooting

### Ошибка "ModuleNotFoundError: No module named 'aiohttp'"

```bash
pip install -r requirements.txt
```

### Ошибка с cryptography на Windows

Установите Microsoft C++ Build Tools:  
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Или используйте Docker:

```bash
docker-compose up -d
```

### Ошибка "Python 3.13/3.15 не поддерживается"

Установите Python 3.12: https://www.python.org/downloads/release/python-3120/
