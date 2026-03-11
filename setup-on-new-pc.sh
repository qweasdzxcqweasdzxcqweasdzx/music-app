#!/bin/bash
# Скрипт автоматической настройки Ultimate Music App на новом ПК

set -e

echo "============================================"
echo "🚀 Настройка Ultimate Music App на новом ПК"
echo "============================================"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Проверка наличия migration_backup
if [ -d "migration_backup" ]; then
    echo "✅ Найдена папка migration_backup"
    BACKUP_DIR="$PROJECT_DIR/migration_backup"
else
    echo "⚠️ Папка migration_backup не найдена"
    BACKUP_DIR=""
fi

# ==================== ПРОВЕРКА СИСТЕМЫ ====================
echo ""
echo "🔍 Шаг 1: Проверка системы..."

# Проверка Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 не найден"
    echo "Установите: sudo apt install python3.12 python3.12-venv python3-pip"
    exit 1
fi

# Проверка Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION"
else
    echo "❌ Node.js не найден"
    echo "Установите: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
fi

# Проверка Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✅ $GIT_VERSION"
else
    echo "❌ Git не найден"
    echo "Установите: sudo apt install -y git"
    exit 1
fi

# Проверка MongoDB
if command -v mongod &> /dev/null; then
    echo "✅ MongoDB установлена"
    MONGO_STATUS=$(sudo systemctl is-active mongod 2>/dev/null || echo "not running")
    if [ "$MONGO_STATUS" = "active" ]; then
        echo "   Статус: ✓ запущен"
    else
        echo "   Статус: ⚠ не запущен"
        read -p "Запустить MongoDB? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl start mongod
            sudo systemctl enable mongod
            echo "✅ MongoDB запущен"
        fi
    fi
else
    echo "⚠️ MongoDB не найдена (будет работать без БД)"
fi

# Проверка Redis
if command -v redis-server &> /dev/null; then
    echo "✅ Redis установлен"
    REDIS_STATUS=$(sudo systemctl is-active redis 2>/dev/null || echo "not running")
    if [ "$REDIS_STATUS" = "active" ]; then
        echo "   Статус: ✓ запущен"
    else
        echo "   Статус: ⚠ не запущен"
        read -p "Запустить Redis? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl start redis-server
            sudo systemctl enable redis-server
            echo "✅ Redis запущен"
        fi
    fi
else
    echo "⚠️ Redis не найден (будет работать без кэширования)"
fi

# ==================== BACKEND ====================
echo ""
echo "🔧 Шаг 2: Настройка Backend..."

cd "$PROJECT_DIR/backend"

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    echo "✅ venv создано"
else
    echo "✅ venv уже существует"
fi

# Активация venv
source venv/bin/activate

# Установка зависимостей
echo "Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

# Восстановление .env
if [ -n "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/backend.env" ]; then
    echo "Восстановление backend/.env..."
    cp "$BACKUP_DIR/backend.env" .env
    echo "✅ backend/.env восстановлен"
elif [ ! -f ".env" ]; then
    echo "⚠️ .env не найден. Копируем из .env.example..."
    cp .env.example .env
    echo "⚠️ Отредактируйте backend/.env и заполните значения!"
    read -p "Открыть .env в редакторе? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
fi

# ==================== FRONTEND ====================
echo ""
echo "🎨 Шаг 3: Настройка Frontend..."

cd "$PROJECT_DIR/frontend"

# Установка Node.js зависимостей
if [ ! -d "node_modules" ]; then
    echo "Установка npm зависимостей..."
    npm install
    echo "✅ Зависимости установлены"
else
    echo "✅ node_modules уже существует"
    read -p "Обновить зависимости? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install
        echo "✅ Зависимости обновлены"
    fi
fi

# Восстановление .env
if [ -n "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/frontend.env" ]; then
    echo "Восстановление frontend/.env..."
    cp "$BACKUP_DIR/frontend.env" .env
    echo "✅ frontend/.env восстановлен"
elif [ ! -f ".env" ]; then
    echo "Создание frontend/.env..."
    echo "VITE_API_URL=http://localhost:8081/api" > .env
    echo "✅ frontend/.env создан"
fi

# ==================== БАЗА ДАННЫХ ====================
echo ""
echo "🗄️ Шаг 4: Восстановление базы данных..."

if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR/mongodb" ]; then
    read -p "Импортировать базу данных из бэкапа? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v mongorestore &> /dev/null; then
            echo "Импорт MongoDB..."
            mongorestore --uri="mongodb://localhost:27017" --db=ultimate_music_app "$BACKUP_DIR/mongodb/ultimate_music_app"
            echo "✅ MongoDB импортирована"
        else
            echo "⚠️ mongorestore не найден"
        fi
    fi
else
    echo "⚠️ Бэкап MongoDB не найден. База будет создана автоматически."
fi

# ==================== МУЗЫКАЛЬНАЯ БИБЛИОТЕКА ====================
echo ""
echo "🎵 Шаг 5: Восстановление музыкальной библиотеки..."

if [ -n "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/music_library.tar.gz" ]; then
    read -p "Распаковать музыкальную библиотеку? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Распаковка..."
        cd "$PROJECT_DIR/backend"
        tar -xzvf "$BACKUP_DIR/music_library.tar.gz"
        echo "✅ Музыкальная библиотека распакована"
    fi
else
    echo "⚠️ Бэкап музыки не найден"
fi

# ==================== ТЕСТОВЫЙ ЗАПУСК ====================
echo ""
echo "🧪 Шаг 6: Тестовый запуск..."

cd "$PROJECT_DIR/backend"
source venv/bin/activate

echo "Проверка конфигурации..."
python -c "from config import settings; print('✅ Конфигурация загружена')" 2>/dev/null || echo "⚠️ Ошибка конфигурации"

echo ""
echo "============================================"
echo "✅ НАСТРОЙКА ЗАВЕРШЕНА!"
echo "============================================"
echo ""
echo "📂 Путь к проекту: $PROJECT_DIR"
echo ""
echo "🚀 ЗАПУСК ПРОЕКТА:"
echo ""
echo "1. Backend (терминал 1):"
echo "   cd $PROJECT_DIR/backend"
echo "   source venv/bin/activate"
echo "   python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000"
echo ""
echo "2. CORS Proxy (терминал 2):"
echo "   cd $PROJECT_DIR/backend"
echo "   source venv/bin/activate"
echo "   python cors_proxy_8081.py"
echo ""
echo "3. Cloudflare Tunnel (терминал 3):"
echo "   cloudflared tunnel --url http://localhost:8081"
echo ""
echo "4. Frontend (разработка, терминал 4):"
echo "   cd $PROJECT_DIR/frontend"
echo "   npm run dev"
echo ""
echo "============================================"
echo ""
echo "📖 Документация:"
echo "   - MIGRATION_GUIDE.md - полное руководство"
echo "   - backend/README.md - backend документация"
echo "   - frontend/README.md - frontend документация"
echo ""
echo "============================================"
