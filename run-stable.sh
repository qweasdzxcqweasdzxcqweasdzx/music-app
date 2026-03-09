#!/bin/bash
# 🚀 БЫСТРЫЙ СТАБИЛЬНЫЙ ЗАПУСК
# Использует Cloudflare Quick Tunnel с авто-перезапуском

set -e

echo "🚀 Стабильный запуск Music App"
echo "=============================="
echo ""

APP_DIR="/home/c1ten12/music-app"
LOG_DIR="/tmp/music-app"
PID_DIR="/tmp/music-app/pids"

mkdir -p $LOG_DIR $PID_DIR

# Остановка старого
echo "📋 Остановка старых процессов..."
pkill -f "uvicorn main_lite" 2>/dev/null || true
pkill -f "cors_proxy_8081" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 2

# Запуск бэкенда
echo ""
echo "🔧 Запуск бэкенда..."
cd $APP_DIR/backend
source venv/bin/activate

nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > $LOG_DIR/backend.log 2>&1 &
echo $! > $PID_DIR/backend.pid

sleep 3
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "  ✅ Бэкенд работает"
else
    echo "  ❌ Бэкенд не запустился"
    exit 1
fi

# Запуск CORS Proxy
echo ""
echo "🔧 Запуск CORS Proxy..."
nohup python cors_proxy_8081.py > $LOG_DIR/cors.log 2>&1 &
echo $! > $PID_DIR/cors.pid

sleep 2
if curl -s http://localhost:8081/api/censorship/test | grep -q "ok"; then
    echo "  ✅ CORS Proxy работает"
else
    echo "  ❌ CORS Proxy не запустился"
    exit 1
fi

# Запуск Cloudflare
echo ""
echo "🌐 Запуск Cloudflare Tunnel..."

nohup /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 > $LOG_DIR/cloudflared.log 2>&1 &
CF_PID=$!
echo $CF_PID > $PID_DIR/cloudflared.pid

echo "  Ожидание подключения (15 сек)..."
sleep 15

# Получение URL
CLOUDFLARE_URL=$(grep "trycloudflare.com" $LOG_DIR/cloudflared.log | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)

if [ -n "$CLOUDFLARE_URL" ]; then
    echo "  ✅ Cloudflare URL: $CLOUDFLARE_URL"
    echo "$CLOUDFLARE_URL" > $LOG_DIR/current_url.txt
else
    echo "  ⚠️  Не удалось получить URL"
    echo "  Проверьте: tail -f $LOG_DIR/cloudflared.log"
fi

# Обновление фронтенда
if [ -n "$CLOUDFLARE_URL" ]; then
    echo ""
    echo "🔄 Обновление фронтенда..."
    
    sed -i "s|const API_URL = .*|const API_URL = '$CLOUDFLARE_URL/api';|" \
        $APP_DIR/frontend/src/api/musicApi.js
    
    sed -i "s|https://[a-zA-Z0-9.-]*trycloudflare.com|$CLOUDFLARE_URL|g" \
        $APP_DIR/frontend/src/pages/Search.jsx
    
    cd $APP_DIR/frontend
    npm run build > $LOG_DIR/build.log 2>&1
    
    echo "  ✅ Фронтенд обновлён"
fi

# Итог
echo ""
echo "=============================="
echo "✅ ЗАПУЩЕНО!"
echo ""
echo "📊 Статус:"
echo "  Бэкенд:  http://localhost:8000 ✅"
echo "  CORS:    http://localhost:8081 ✅"
if [ -n "$CLOUDFLARE_URL" ]; then
    echo "  Cloud:   $CLOUDFLARE_URL"
fi
echo ""
echo "📱 Локально:"
echo "  http://localhost:8000/static/local-test.html"
echo ""
echo "🔗 Для Telegram:"
if [ -n "$CLOUDFLARE_URL" ]; then
    echo "  $CLOUDFLARE_URL"
    echo ""
    echo "  ⚠️  Quick Tunnel может отключаться!"
    echo "  Для стабильности используйте:"
    echo "    ./setup-named-tunnel.sh  (с доменом)"
    echo "  или"
    echo "    ngrok http 8081  (без домена, стабильнее)"
else
    echo "  Настройте туннель:"
    echo "    ./setup-named-tunnel.sh"
fi
echo ""
echo "📁 Логи:"
echo "  tail -f $LOG_DIR/backend.log"
echo "  tail -f $LOG_DIR/cors.log"
echo "  tail -f $LOG_DIR/cloudflared.log"
echo ""
echo "🛑 Остановка:"
echo "  $APP_DIR/stop.sh"
echo "=============================="
