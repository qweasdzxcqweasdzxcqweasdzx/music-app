#!/bin/bash
# 🚀 БЫСТРЫЙ ДЕПЛОЙ MUSIC APP НА СЕРВЕРЕ

set -e

echo "🚀 Music App - Быстрый деплой на сервере"
echo "========================================"
echo ""

APP_DIR="/home/c1ten12/music-app"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ==================== Проверка ====================
echo "📋 Проверка системы..."

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3:$(python3 --version)${NC}"

# Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js:$(node --version)${NC}"

# Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git не найден, устанавливаем...${NC}"
    sudo apt update && sudo apt install -y git
fi

# Cloudflared
if [ ! -f "/home/c1ten12/bin/cloudflared" ]; then
    echo -e "${YELLOW}⚠️  Cloudflared не найден, устанавливаем...${NC}"
    mkdir -p /home/c1ten12/bin
    curl -L --output /tmp/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x /tmp/cloudflared
    mv /tmp/cloudflared /home/c1ten12/bin/cloudflared
fi
echo -e "${GREEN}✅ Cloudflared установлен${NC}"

# ==================== Зависимости ====================
echo ""
echo "📦 Установка зависимостей..."

# Python зависимости
cd $BACKEND_DIR
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения Python..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Установка Python зависимостей..."
pip install --upgrade pip -q
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi
echo -e "${GREEN}✅ Python зависимости установлены${NC}"

# Node.js зависимости
cd $FRONTEND_DIR
echo "Установка Node.js зависимостей..."
npm install --silent
echo -e "${GREEN}✅ Node.js зависимости установлены${NC}"

# Сборка фронтенда
echo "Сборка фронтенда..."
npm run build --silent
echo -e "${GREEN}✅ Фронтенд собран${NC}"

# ==================== Cloudflare Tunnel ====================
echo ""
echo "🌐 Настройка Cloudflare Tunnel..."

# Проверка авторизации
if [ ! -f "$HOME/.cloudflared/cert.pem" ]; then
    echo -e "${YELLOW}⚠️  Cloudflare не авторизован${NC}"
    echo ""
    echo "1. Откройте: https://dash.teams.cloudflare.com/"
    echo "2. Zero Trust → Network → Tunnels → Create tunnel"
    echo "3. Имя: music-app-tunnel"
    echo "4. Скопируйте токен"
    echo ""
    read -p "Вставьте токен Cloudflare: " TUNNEL_TOKEN
    
    if [ -n "$TUNNEL_TOKEN" ]; then
        /home/c1ten12/bin/cloudflared tunnel login --token $TUNNEL_TOKEN
        echo -e "${GREEN}✅ Cloudflare авторизован${NC}"
    else
        echo -e "${YELLOW}⚠️  Пропускаем авторизацию${NC}"
    fi
fi

# Создание туннеля
TUNNEL_NAME="music-app-tunnel"
if [ ! -f "$HOME/.cloudflared/$TUNNEL_NAME.json" ]; then
    echo "Создание туннеля..."
    /home/c1ten12/bin/cloudflared tunnel create $TUNNEL_NAME
    echo -e "${GREEN}✅ Туннель создан${NC}"
fi

# Конфигурация
CONFIG_FILE="$HOME/.cloudflared/$TUNNEL_NAME.yml"
cat > $CONFIG_FILE << EOF
tunnel: $TUNNEL_NAME
credentials-file: $HOME/.cloudflared/$TUNNEL_NAME.json

ingress:
  - hostname: api.YOUR_DOMAIN.com
    service: http://localhost:8081
  - hostname: app.YOUR_DOMAIN.com
    service: http://localhost:8000
  - service: http_status:404
EOF

echo -e "${YELLOW}⚠️  Отредактируйте конфиг: $CONFIG_FILE${NC}"
echo "   Замените YOUR_DOMAIN.com на ваш домен"

# ==================== Systemd сервисы ====================
echo ""
echo "🔧 Настройка systemd сервисов..."

if [ -f "$APP_DIR/music-app-backend.service" ]; then
    echo "Копирование сервисов..."
    sudo cp $APP_DIR/music-app-backend.service /etc/systemd/system/
    sudo cp $APP_DIR/music-app-cors.service /etc/systemd/system/
    sudo cp $APP_DIR/music-app-cloudflared.service /etc/systemd/system/
    
    echo "Перезагрузка systemd..."
    sudo systemctl daemon-reload
    
    echo "Включение сервисов..."
    sudo systemctl enable music-app-backend
    sudo systemctl enable music-app-cors
    sudo systemctl enable music-app-cloudflared
    
    echo -e "${GREEN}✅ Systemd сервисы настроены${NC}"
else
    echo -e "${RED}❌ Файлы сервисов не найдены${NC}"
fi

# ==================== .env файл ====================
echo ""
echo "🔐 Настройка окружения..."

cd $BACKEND_DIR
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Создан .env файл"
        echo -e "${YELLOW}⚠️  Отредактируйте .env и заполните секреты${NC}"
    fi
else
    echo -e "${GREEN}✅ .env уже существует${NC}"
fi

# ==================== Запуск ====================
echo ""
echo "🚀 Запуск сервисов..."

sudo systemctl start music-app-backend
sudo systemctl start music-app-cors
sudo systemctl start music-app-cloudflared

sleep 5

# Проверка
echo ""
echo "📊 Проверка статуса..."

if sudo systemctl is-active --quiet music-app-backend; then
    echo -e "${GREEN}✅ Бэкенд запущен${NC}"
else
    echo -e "${RED}❌ Бэкенд не запустился${NC}"
fi

if sudo systemctl is-active --quiet music-app-cors; then
    echo -e "${GREEN}✅ CORS Proxy запущен${NC}"
else
    echo -e "${RED}❌ CORS Proxy не запустился${NC}"
fi

if sudo systemctl is-active --quiet music-app-cloudflared; then
    echo -e "${GREEN}✅ Cloudflare Tunnel запущен${NC}"
else
    echo -e "${RED}❌ Cloudflare Tunnel не запустился${NC}"
fi

# ==================== Итог ====================
echo ""
echo "========================================"
echo -e "${GREEN}✅ ДЕПЛОЙ ЗАВЕРШЁН!${NC}"
echo ""
echo "📊 Статус сервисов:"
echo "  sudo systemctl status music-app-*"
echo ""
echo "📁 Логи:"
echo "  sudo journalctl -u music-app-backend -f"
echo "  sudo journalctl -u music-app-cors -f"
echo "  sudo journalctl -u music-app-cloudflared -f"
echo ""
echo "🌐 DNS настройка:"
echo "  1. Добавьте домен в Cloudflare"
echo "  2. Измените NS серверы у регистратора"
echo "  3. В Cloudflare Tunnel добавьте hostnames:"
echo "     - api.YOUR_DOMAIN.com → http://localhost:8081"
echo "     - app.YOUR_DOMAIN.com → http://localhost:8000"
echo ""
echo "🔗 URL после настройки DNS:"
echo "  https://app.YOUR_DOMAIN.com"
echo "  https://api.YOUR_DOMAIN.com"
echo ""
echo "📖 Полная инструкция:"
echo "  $APP_DIR/FULL_DEPLOYMENT.md"
echo "========================================"
