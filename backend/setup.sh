#!/bin/bash
# Скрипт установки зависимостей для Ultimate Music App

echo "=========================================="
echo "  Ultimate Music App - Setup Script"
echo "=========================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден"
    exit 1
fi

echo ""
echo "📦 Установка зависимостей backend..."
echo ""

cd "$(dirname "$0")"

# Установка зависимостей
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Зависимости установлены успешно"
else
    echo ""
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

echo ""
echo "📋 Проверка конфигурации..."
echo ""

# Проверка .env
if [ ! -f ".env" ]; then
    echo "⚠️  .env не найден. Копируем из .env.example..."
    cp .env.example .env
    echo "✅ .env создан. Отредактируйте его для указания ключей API."
else
    echo "✅ .env найден"
fi

echo ""
echo "=========================================="
echo "  Setup завершён!"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Отредактируйте .env и укажите:"
echo "   - SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET"
echo "   - SECRET_KEY (сгенерируйте случайную строку)"
echo "   - TELEGRAM_BOT_TOKEN (опционально)"
echo ""
echo "2. Запустите MongoDB и Redis:"
echo "   docker run -d -p 27017:27017 --name music_mongo mongo:7"
echo "   docker run -d -p 6379:6379 --name music_redis redis:7-alpine"
echo ""
echo "3. Или используйте Docker Compose:"
echo "   docker-compose up -d"
echo ""
echo "4. Запустите сервер:"
echo "   uvicorn main:app --reload"
echo ""
echo "5. Откройте http://localhost:8000/docs"
echo ""
