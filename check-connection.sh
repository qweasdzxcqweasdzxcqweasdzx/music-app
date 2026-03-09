#!/bin/bash
# Получить текущий Cloudflare URL

echo "🔍 Проверка связи Фронтенд-Бэкенд"
echo "=================================="
echo ""

# Проверка бэкенда
echo -n "Бэкенд (порт 8000): "
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Работает"
else
    echo "❌ Не работает"
fi

# Проверка CORS proxy
echo -n "CORS Proxy (порт 8081): "
if curl -s http://localhost:8081/api/censorship/test | grep -q "ok"; then
    echo "✅ Работает"
else
    echo "❌ Не работает"
fi

# Проверка Cloudflare
echo ""
echo "Cloudflare Tunnel:"

# Получаем URL из musicApi.js
CURRENT_URL=$(grep "const API_URL" /home/c1ten12/music-app/frontend/src/api/musicApi.js | sed "s/.*'\(.*\)'.*/\1/" | sed 's/\/api$//')

if [ -n "$CURRENT_URL" ]; then
    echo "  URL из фронтенда: $CURRENT_URL"
    
    # Проверяем работу
    if curl -s --max-time 3 "$CURRENT_URL/api/censorship/test" | grep -q "ok"; then
        echo "  Статус: ✅ Работает"
    else
        echo "  Статус: ⚠️  Не отвечает (Cloudflare Quick Tunnel нестабилен)"
    fi
else
    echo "  ❌ URL не найден"
fi

echo ""
echo "=================================="
echo "📡 Локальные URL (всегда работают):"
echo "  Backend:    http://localhost:8000"
echo "  CORS Proxy: http://localhost:8081"
echo "  Swagger:    http://localhost:8000/docs"
echo ""
echo "🔧 Команды для проверки:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8081/api/censorship/test"
echo "  curl 'http://localhost:8081/api/censorship/search-uncensored?q=eminem'"
echo ""

# Проверка процессов
echo "📊 Процессы:"
ps aux | grep -E "(cloudflared|uvicorn|cors_proxy)" | grep -v grep | awk '{print "  " $11 " " $12 " " $13}'

echo ""
echo "=================================="
echo "💡 Для перезапуска Cloudflare:"
echo "  ./fix-connection.sh"
