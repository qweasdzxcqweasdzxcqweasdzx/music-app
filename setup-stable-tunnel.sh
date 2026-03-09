#!/bin/bash
# Стабильный HTTPS для Telegram через Cloudflare Named Tunnel

set -e

TUNNEL_NAME="music-app-tunnel"
CONFIG_FILE="$HOME/.cloudflared/$TUNNEL_NAME.yml"

echo "🔧 Настройка стабильного Cloudflare Tunnel"
echo "==========================================="
echo ""

# Проверка авторизации
if [ ! -f "$HOME/.cloudflared/cert.pem" ]; then
    echo "⚠️  Требуется авторизация в Cloudflare"
    echo ""
    echo "1. Откройте: https://dash.teams.cloudflare.com/"
    echo "2. Залогиньтесь"
    echo "3. Access → Tunnels → Create Tunnel"
    echo "4. Выберите 'Cloudflare' как тип"
    echo "5. Дайте имя: $TUNNEL_NAME"
    echo "6. Скопируйте токен"
    echo ""
    read -p "Вставьте токен туннеля: " TUNNEL_TOKEN
    
    echo "Авторизация..."
    /home/c1ten12/bin/cloudflared tunnel login --token $TUNNEL_TOKEN
fi

# Создание туннеля если не существует
if [ ! -f "$HOME/.cloudflared/$TUNNEL_NAME.json" ]; then
    echo "Создание туннеля..."
    /home/c1ten12/bin/cloudflared tunnel create $TUNNEL_NAME
fi

# Создание конфига
echo "Настройка конфига..."
mkdir -p $HOME/.cloudflared

cat > $CONFIG_FILE << EOF
tunnel: $TUNNEL_NAME
credentials-file: $HOME/.cloudflared/$TUNNEL_NAME.json

ingress:
  - hostname: music.YOUR_DOMAIN.com
    service: http://localhost:8000
  - hostname: music-api.YOUR_DOMAIN.com
    service: http://localhost:8081
  - service: http_status:404
EOF

echo ""
echo "✅ Конфиг создан: $CONFIG_FILE"
echo ""
echo "📝 ТЕПЕРЬ НУЖНО:"
echo "1. Зайдите в Cloudflare Dashboard"
echo "2. Access → Tunnels → $TUNNEL_NAME"
echo "3. Add Public Hostname"
echo "4. Добавьте:"
echo "   - Subdomain: music"
echo "   - Domain: YOUR_DOMAIN.com"
echo "   - Service: http://localhost:8000"
echo "   - Subdomain: music-api"  
echo "   - Domain: YOUR_DOMAIN.com"
echo "   - Service: http://localhost:8081"
echo ""
read -p "Нажмите Enter когда настроите..."

# Запуск туннеля
echo ""
echo "🚀 Запуск туннеля..."
nohup /home/c1ten12/bin/cloudflared tunnel run $TUNNEL_NAME > /tmp/cloudflared-named.log 2>&1 &
echo $! > /tmp/cloudflared-named.pid

sleep 5
echo ""
echo "✅ Туннель запущен!"
echo ""
echo "Проверка статуса:"
echo "  systemctl status cloudflared-$TUNNEL_NAME"
echo "  или"
echo "  ps aux | grep cloudflared"
