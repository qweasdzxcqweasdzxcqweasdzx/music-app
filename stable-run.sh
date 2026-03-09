#!/bin/bash
# 🚀 STABLE RUN - Стабильный запуск Music App для Telegram

set -e

echo "🎵 Music App - Стабильный запуск для Telegram"
echo "=============================================="
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Пути
APP_DIR="/home/c1ten12/music-app"
BACKEND_DIR="$APP_DIR/backend"
LOG_DIR="/tmp/music-app"
PID_DIR="/tmp/music-app/pids"

# Создаем директории
mkdir -p $LOG_DIR $PID_DIR

# Функция проверки порта
check_port() {
    local port=$1
    lsof -i :$port > /dev/null 2>&1
    return $?
}

# Функция проверки процесса
check_process() {
    local pattern=$1
    pgrep -f "$pattern" > /dev/null 2>&1
    return $?
}

# ==================== Остановка старых процессов ====================
echo "📋 Остановка старых процессов..."

if check_process "uvicorn main_lite"; then
    pkill -f "uvicorn main_lite" && echo "  ✅ Бэкенд остановлен"
fi

if check_process "cors_proxy_8081"; then
    pkill -f "cors_proxy_8081" && echo "  ✅ CORS Proxy остановлен"
fi

if check_process "cloudflared tunnel"; then
    pkill -f "cloudflared tunnel" && echo "  ✅ Cloudflare остановлен"
fi

sleep 2

# ==================== Запуск бэкенда ====================
echo ""
echo "🔧 Запуск бэкенда (порт 8000)..."

cd $BACKEND_DIR
source venv/bin/activate

nohup python -m uvicorn main_lite:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload > $LOG_DIR/backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > $PID_DIR/backend.pid
echo "  ✅ Бэкенд запущен (PID: $BACKEND_PID)"

# Проверка
sleep 3
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "  ${GREEN}✅ Бэкенд работает${NC}"
else
    echo -e "  ${RED}❌ Бэкенд не запустился${NC}"
    tail -20 $LOG_DIR/backend.log
    exit 1
fi

# ==================== Запуск CORS Proxy ====================
echo ""
echo "🔧 Запуск CORS Proxy (порт 8081)..."

nohup python cors_proxy_8081.py > $LOG_DIR/cors.log 2>&1 &

CORS_PID=$!
echo $CORS_PID > $PID_DIR/cors.pid
echo "  ✅ CORS Proxy запущен (PID: $CORS_PID)"

# Проверка
sleep 2
if curl -s http://localhost:8081/api/censorship/test | grep -q "ok"; then
    echo -e "  ${GREEN}✅ CORS Proxy работает${NC}"
else
    echo -e "  ${RED}❌ CORS Proxy не запустился${NC}"
    tail -20 $LOG_DIR/cors.log
    exit 1
fi

# ==================== Запуск Cloudflare Tunnel ====================
echo ""
echo "🌐 Запуск Cloudflare Tunnel..."

# Останавливаем старый туннель
pkill -f cloudflared 2>/dev/null || true
sleep 2

# Запускаем новый туннель для CORS proxy
nohup /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 > $LOG_DIR/cloudflared.log 2>&1 &

CF_PID=$!
echo $CF_PID > $PID_DIR/cloudflared.pid
echo "  ✅ Cloudflare запущен (PID: $CF_PID)"

# Ждем получения URL
sleep 12

# Получаем URL
CLOUDFLARE_URL=$(grep "trycloudflare.com" $LOG_DIR/cloudflared.log | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)

if [ -n "$CLOUDFLARE_URL" ]; then
    echo -e "  ${GREEN}✅ Cloudflare URL: $CLOUDFLARE_URL${NC}"
else
    echo -e "  ${YELLOW}⚠️  Cloudflare URL не получен, проверяем логи...${NC}"
    tail -10 $LOG_DIR/cloudflared.log
fi

# ==================== Обновление фронтенда ====================
echo ""
echo "🔄 Обновление фронтенда..."

if [ -n "$CLOUDFLARE_URL" ]; then
    # Обновляем API URL
    sed -i "s|const API_URL = .*|const API_URL = '$CLOUDFLARE_URL/api';|" \
        $BACKEND_DIR/../frontend/src/api/musicApi.js
    
    sed -i "s|https://[a-zA-Z0-9.-]*trycloudflare.com|$CLOUDFLARE_URL|g" \
        $BACKEND_DIR/../frontend/src/pages/Search.jsx
    
    # Собираем фронтенд
    cd $BACKEND_DIR/../frontend
    npm run build > $LOG_DIR/build.log 2>&1
    
    echo "  ✅ Фронтенд обновлён"
fi

# ==================== Итоговая информация ====================
echo ""
echo "=============================================="
echo -e "${GREEN}✅ ВСЁ ЗАПУЩЕНО!${NC}"
echo ""
echo "📊 Статус сервисов:"
echo "  Бэкенд:    http://localhost:8000 ${GREEN}●${NC}"
echo "  CORS:      http://localhost:8081 ${GREEN}●${NC}"
echo "  Cloudflare: $CLOUDFLARE_URL ${GREEN}●${NC}"
echo ""
echo "🔗 URL для Telegram:"
echo "  $CLOUDFLARE_URL"
echo ""
echo "📱 Локальная тестовая страница:"
echo "  http://localhost:8000/static/local-test.html"
echo ""
echo "📋 Swagger API:"
echo "  http://localhost:8000/docs"
echo ""
echo "📁 Логи:"
echo "  Бэкенд:  tail -f $LOG_DIR/backend.log"
echo "  CORS:    tail -f $LOG_DIR/cors.log"
echo "  Cloud:   tail -f $LOG_DIR/cloudflared.log"
echo ""
echo "🛑 Остановка:"
echo "  $APP_DIR/stop.sh"
echo ""
echo "🔄 Перезапуск:"
echo "  $APP_DIR/stable-run.sh"
echo "=============================================="

# Сохраняем URL
echo "$CLOUDFLARE_URL" > $LOG_DIR/current_url.txt

# Открываем браузер (если возможно)
# xdg-open "http://localhost:8000/static/local-test.html" 2>/dev/null || true
