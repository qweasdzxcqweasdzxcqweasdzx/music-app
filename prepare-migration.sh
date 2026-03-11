#!/bin/bash
# Скрипт подготовки проекта к переносу на другой ПК

set -e

echo "============================================"
echo "🚀 Подготовка Ultimate Music App к переносу"
echo "============================================"
echo ""

PROJECT_DIR="/home/c1ten12/music-app"
BACKUP_DIR="$PROJECT_DIR/migration_backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cd "$PROJECT_DIR"

# Создание директории для бэкапа
echo "📁 Создание директории для бэкапа..."
mkdir -p "$BACKUP_DIR"

# 1. Git commit и push
echo ""
echo "📦 Шаг 1: Git commit и push..."
read -p "Закоммитить и запушить все изменения? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git status
    
    read -p "Добавить все изменения? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Migration backup: $TIMESTAMP" || echo "Нет изменений для коммита"
    fi
    
    read -p "Запушить в GitHub? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo "✅ Git push завершён"
    fi
else
    echo "⏭️ Пропуск Git операций"
fi

# 2. Сохранение .env файлов
echo ""
echo "📄 Шаг 2: Сохранение .env файлов..."

if [ -f "$PROJECT_DIR/backend/.env" ]; then
    echo "Сохранение backend/.env..."
    cp "$PROJECT_DIR/backend/.env" "$BACKUP_DIR/backend.env"
    echo "✅ backend/.env сохранён"
else
    echo "⚠️ backend/.env не найден"
fi

if [ -f "$PROJECT_DIR/frontend/.env" ]; then
    echo "Сохранение frontend/.env..."
    cp "$PROJECT_DIR/frontend/.env" "$BACKUP_DIR/frontend.env"
    echo "✅ frontend/.env сохранён"
else
    echo "⚠️ frontend/.env не найден"
fi

# 3. Экспорт MongoDB
echo ""
echo "🗄️ Шаг 3: Экспорт MongoDB (опционально)..."
read -p "Экспортировать базу данных? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v mongodump &> /dev/null; then
        echo "Экспорт MongoDB..."
        mkdir -p "$BACKUP_DIR/mongodb"
        mongodump --uri="mongodb://localhost:27017" --db=ultimate_music_app --out="$BACKUP_DIR/mongodb"
        echo "✅ MongoDB экспортирована в $BACKUP_DIR/mongodb"
    else
        echo "⚠️ mongodump не найден. Установите MongoDB tools."
    fi
else
    echo "⏭️ Пропуск экспорта MongoDB"
fi

# 4. Сохранение музыкальной библиотеки
echo ""
echo "🎵 Шаг 4: Музыкальная библиотека (опционально)..."
if [ -d "$PROJECT_DIR/backend/music_library" ]; then
    LIBRARY_SIZE=$(du -sh "$PROJECT_DIR/backend/music_library" 2>/dev/null | cut -f1)
    echo "Размер music_library: $LIBRARY_SIZE"
    
    read -p "Создать архив с музыкальной библиотекой? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Создание архива..."
        tar -czvf "$BACKUP_DIR/music_library.tar.gz" -C "$PROJECT_DIR/backend" music_library
        echo "✅ Музыкальная библиотека сохранена"
    fi
else
    echo "⚠️ music_library не найдена"
fi

# 5. Сохранение информации о системе
echo ""
echo "💾 Шаг 5: Сохранение информации о системе..."
cat > "$BACKUP_DIR/system_info.txt" << EOF
Дата экспорта: $(date)
Пользователь: $(whoami)
Хост: $(hostname)

Python версия:
$(python3 --version 2>/dev/null || echo "Python не найден")

Node.js версия:
$(node --version 2>/dev/null || echo "Node.js не найден")

Git версия:
$(git --version 2>/dev/null || echo "Git не найден")

MongoDB версия:
$(mongod --version 2>/dev/null | head -1 || echo "MongoDB не найдена")

Redis версия:
$(redis-server --version 2>/dev/null | head -1 || echo "Redis не найден")

Git remote URL:
$(git remote get-url origin 2>/dev/null || echo "Git remote не найден")

Последний коммит:
$(git log -1 --oneline 2>/dev/null || echo "Нет коммитов")
EOF
echo "✅ system_info.txt сохранён"

# 6. Создание README для миграции
echo ""
echo "📝 Шаг 6: Создание инструкции для нового ПК..."
cat > "$BACKUP_DIR/READ_ME_FIRST.txt" << EOF
============================================
🎵 ULTIMATE MUSIC APP - ПЕРЕНOS НА НОВЫЙ ПК
============================================

Дата экспорта: $(date)

📁 СОДЕРЖИМОЕ ЭТОЙ ПАПКИ:
- backend.env - ваш backend .env файл
- frontend.env - ваш frontend .env файл
- mongodb/ - экспорт базы данных (если создавали)
- music_library.tar.gz - музыкальная библиотека (если создавали)
- system_info.txt - информация о старой системе

📋 СЛЕДУЮЩИЕ ШАГИ:

1. На новом ПК:
   git clone https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app.git
   cd music-app

2. Скопируйте .env файлы:
   cp migration_backup/backend.env backend/.env
   cp migration_backup/frontend.env frontend/.env

3. Установите зависимости:
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install

4. Импортируйте базу данных (если экспортировали):
   mongorestore --uri="mongodb://localhost:27017" --db=ultimate_music_app migration_backup/mongodb/ultimate_music_app

5. Распакуйте музыку (если создавали архив):
   cd backend
   tar -xzvf ../migration_backup/music_library.tar.gz

6. Запустите проект:
   # Backend (порт 8000)
   cd backend
   source venv/bin/activate
   python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
   
   # CORS Proxy (порт 8081)
   cd backend
   source venv/bin/activate
   python cors_proxy_8081.py &
   
   # Cloudflare Tunnel (HTTPS)
   cloudflared tunnel --url http://localhost:8081

7. Проверьте работу:
   curl http://localhost:8000/health
   curl http://localhost:8081/api/censorship/test

📖 ПОЛНАЯ ИНСТРУКЦИЯ:
   Откройте MIGRATION_GUIDE.md в корне проекта

============================================
EOF
echo "✅ READ_ME_FIRST.txt создан"

# 7. Вывод информации
echo ""
echo "============================================"
echo "✅ ПОДГОТОВКА ЗАВЕРШЕНА!"
echo ""
echo "📁 Бэкап создан в: $BACKUP_DIR"
echo ""
echo "📋 СОДЕРЖИМОЕ:"
ls -lah "$BACKUP_DIR"
echo ""
echo "============================================"
echo ""
echo "🎯 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1. Скопируйте папку migration_backup на новый ПК"
echo "   (через USB, scp, rsync, облако)"
echo ""
echo "2. На новом ПК выполните:"
echo "   git clone https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app.git"
echo "   cd music-app"
echo "   cp -r migration_backup/* ."
echo ""
echo "3. Следуйте инструкции в READ_ME_FIRST.txt"
echo ""
echo "============================================"
