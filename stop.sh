#!/bin/bash
# 🛑 Остановка Music App

echo "🛑 Остановка Music App..."

# Пути
PID_DIR="/tmp/music-app/pids"

# Остановка по PID файлам
if [ -f "$PID_DIR/cloudflared.pid" ]; then
    kill $(cat $PID_DIR/cloudflared.pid) 2>/dev/null && echo "  ✅ Cloudflare остановлен"
    rm $PID_DIR/cloudflared.pid
fi

if [ -f "$PID_DIR/cors.pid" ]; then
    kill $(cat $PID_DIR/cors.pid) 2>/dev/null && echo "  ✅ CORS Proxy остановлен"
    rm $PID_DIR/cors.pid
fi

if [ -f "$PID_DIR/backend.pid" ]; then
    kill $(cat $PID_DIR/backend.pid) 2>/dev/null && echo "  ✅ Бэкенд остановлен"
    rm $PID_DIR/backend.pid
fi

# Дополнительная очистка
pkill -f "uvicorn main_lite" 2>/dev/null
pkill -f "cors_proxy_8081" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null

echo ""
echo "✅ Все сервисы остановлены"
