#!/bin/bash
# 🌐 СТАБИЛЬНЫЙ ТУННЕЛЬ - Cloudflare Named Tunnel
# Работает стабильнее Quick Tunnel, бесплатно

set -e

echo "🌐 Настройка стабильного Cloudflare Tunnel"
echo "=========================================="
echo ""

TUNNEL_NAME="music-app"
CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/$TUNNEL_NAME.yml"
CRED_FILE="$CONFIG_DIR/$TUNNEL_NAME.json"

# Создаем директорию
mkdir -p $CONFIG_DIR

# Шаг 1: Авторизация
echo "📝 ШАГ 1: Авторизация в Cloudflare"
echo ""
echo "1. Откройте: https://dash.teams.cloudflare.com/"
echo "2. Зарегистрируйтесь/войдите (бесплатно)"
echo "3. Access → Tunnels → Create tunnel"
echo "4. Выберите 'Cloudflare' как тип"
echo "5. Введите имя: $TUNNEL_NAME"
echo "6. Нажмите 'Save tunnel'"
echo "7. Скопируйте токен (длинная строка)"
echo ""

read -p "Вставьте токен туннеля: " TUNNEL_TOKEN

if [ -z "$TUNNEL_TOKEN" ]; then
    echo "❌ Токен не введён"
    exit 1
fi

echo "Авторизация..."
/home/c1ten12/bin/cloudflared tunnel login --token $TUNNEL_TOKEN

echo ""
echo "✅ Авторизация успешна"

# Шаг 2: Создание туннеля
echo ""
echo "📝 ШАГ 2: Создание туннеля"

if [ -f "$CRED_FILE" ]; then
    echo "⚠️  Туннель уже существует. Удаляем старый..."
    /home/c1ten12/bin/cloudflared tunnel delete $TUNNEL_NAME -f 2>/dev/null || true
fi

echo "Создание туннеля '$TUNNEL_NAME'..."
/home/c1ten12/bin/cloudflared tunnel create $TUNNEL_NAME

echo "✅ Туннель создан"

# Шаг 3: Настройка конфига
echo ""
echo "📝 ШАГ 3: Настройка конфигурации"

cat > $CONFIG_FILE << EOF
tunnel: $TUNNEL_NAME
credentials-file: $CRED_FILE

# Логирование
log-level: info

# ingress - маршрутизация
ingress:
  # CORS Proxy (основной)
  - hostname: music-api.YOUR_DOMAIN.com
    service: http://localhost:8081
    
  # Бэкенд (опционально)
  - hostname: music.YOUR_DOMAIN.com
    service: http://localhost:8000
    
  # По умолчанию - ошибка
  - service: http_status:404
EOF

echo "✅ Конфиг создан: $CONFIG_FILE"

# Шаг 4: Настройка в Cloudflare Dashboard
echo ""
echo "📝 ШАГ 4: Настройка DNS в Cloudflare"
echo ""
echo "1. Зайдите в Cloudflare Dashboard"
echo "2. Выберите ваш домен"
echo "3. DNS → Add record"
echo "4. Добавьте записи:"
echo ""
echo "   Запись 1:"
echo "   - Type: CNAME"
echo "   - Name: music-api"
echo "   - Target: $TUNNEL_NAME.cfargotunnel.com"
echo "   - Proxy: Enabled (orange cloud)"
echo ""
echo "   Запись 2 (опционально):"
echo "   - Type: CNAME"
echo "   - Name: music"
echo "   - Target: $TUNNEL_NAME.cfargotunnel.com"
echo "   - Proxy: Enabled"
echo ""

read -p "Нажмите Enter когда настроите DNS..."

# Шаг 5: Запуск туннеля
echo ""
echo "📝 ШАГ 5: Запуск туннеля"

# Останавливаем старый туннель
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 2

echo "Запуск..."
nohup /home/c1ten12/bin/cloudflared tunnel run $TUNNEL_NAME > /tmp/cloudflared-named.log 2>&1 &
echo $! > /tmp/cloudflared-named.pid

sleep 5

# Проверка
if ps -p $(cat /tmp/cloudflared-named.pid) > /dev/null 2>&1; then
    echo "✅ Туннель запущен!"
else
    echo "❌ Не удалось запустить туннель"
    tail -20 /tmp/cloudflared-named.log
    exit 1
fi

# Итог
echo ""
echo "=========================================="
echo "✅ ГОТОВО!"
echo ""
echo "🌐 Ваши URL (после настройки DNS):"
echo "   https://music-api.YOUR_DOMAIN.com"
echo "   https://music.YOUR_DOMAIN.com"
echo ""
echo "📊 Статус:"
echo "   ps aux | grep cloudflared"
echo "   tail -f /tmp/cloudflared-named.log"
echo ""
echo "🛑 Остановка:"
echo "   kill \$(cat /tmp/cloudflared-named.pid)"
echo ""
echo "📝 Автозапуск (опционально):"
echo "   Добавьте в crontab:"
echo "   @reboot /home/c1ten12/bin/cloudflared tunnel run $TUNNEL_NAME"
echo "=========================================="
