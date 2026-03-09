#!/bin/bash
# 📊 Статус Music App

echo "📊 Music App - Статус сервисов"
echo "=============================="
echo ""

# Проверка процессов
echo "🔄 Процессы:"

if pgrep -f "uvicorn main_lite" > /dev/null; then
    echo "  ✅ Бэкенд (PID: $(pgrep -f 'uvicorn main_lite'))"
else
    echo "  ❌ Бэкенд не запущен"
fi

if pgrep -f "cors_proxy_8081" > /dev/null; then
    echo "  ✅ CORS Proxy (PID: $(pgrep -f 'cors_proxy_8081'))"
else
    echo "  ❌ CORS Proxy не запущен"
fi

if pgrep -f "cloudflared tunnel" > /dev/null; then
    echo "  ✅ Cloudflare Tunnel (PID: $(pgrep -f 'cloudflared'))"
else
    echo "  ❌ Cloudflare не запущен"
fi

echo ""
echo "🔗 URL:"

# Локальные URL
echo "  Бэкенд:  http://localhost:8000"
echo "  CORS:    http://localhost:8081"
echo "  Swagger: http://localhost:8000/docs"
echo "  Local:   http://localhost:8000/static/local-test.html"

# Cloudflare URL
if [ -f "/tmp/music-app/current_url.txt" ]; then
    CF_URL=$(cat /tmp/music-app/current_url.txt)
    echo "  Cloud:   $CF_URL"
    
    # Проверка работы
    if curl -s --max-time 3 "$CF_URL/api/censorship/test" | grep -q "ok"; then
        echo "           ${GREEN}● Работает${NC}"
    else
        echo "           ⚠️  Не отвечает"
    fi
fi

echo ""
echo "📋 Проверка endpoints:"

# Health check
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "  ✅ /health"
else
    echo "  ❌ /health"
fi

# CORS test
if curl -s http://localhost:8081/api/censorship/test | grep -q "ok"; then
    echo "  ✅ /api/censorship/test"
else
    echo "  ❌ /api/censorship/test"
fi

echo ""
echo "=============================="
echo "Запуск:  ./stable-run.sh"
echo "Стоп:    ./stop.sh"
