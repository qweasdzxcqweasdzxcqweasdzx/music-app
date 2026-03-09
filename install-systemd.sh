#!/bin/bash
# 📦 Установка systemd сервисов для Music App

echo "📦 Установка systemd сервисов..."
echo ""

APP_DIR="/home/c1ten12/music-app"

# Копирование сервисов
sudo cp $APP_DIR/music-app-backend.service /etc/systemd/system/
sudo cp $APP_DIR/music-app-cors.service /etc/systemd/system/
sudo cp $APP_DIR/music-app-cloudflared.service /etc/systemd/system/

echo "✅ Сервисы скопированы"

# Создание директории для логов
sudo mkdir -p /tmp/music-app
sudo chown c1ten12:c1ten12 /tmp/music-app

# Перезагрузка systemd
sudo systemctl daemon-reload

echo ""
echo "🔧 Включение сервисов..."

sudo systemctl enable music-app-backend
sudo systemctl enable music-app-cors
sudo systemctl enable music-app-cloudflared

echo ""
echo "🚀 Запуск сервисов..."

sudo systemctl start music-app-backend
sudo systemctl start music-app-cors
sudo systemctl start music-app-cloudflared

echo ""
echo "✅ Сервисы запущены!"
echo ""
echo "📊 Статус:"
echo "  systemctl status music-app-backend"
echo "  systemctl status music-app-cors"
echo "  systemctl status music-app-cloudflared"
echo ""
echo "📁 Логи:"
echo "  journalctl -u music-app-backend -f"
echo "  journalctl -u music-app-cors -f"
echo "  journalctl -u music-app-cloudflared -f"
echo ""
echo "🛑 Остановка:"
echo "  sudo systemctl stop music-app-backend"
echo "  sudo systemctl stop music-app-cors"
echo "  sudo systemctl stop music-app-cloudflared"
