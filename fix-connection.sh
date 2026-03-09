#!/bin/bash
# Фикс связи фронтенд-бэкенд с проверкой и авто-перезапуском

echo "🔧 Fix Connection - Проверка и восстановление связи"
echo "===================================================="

# Функция проверки бэкенда
check_backend() {
    curl -s http://localhost:8000/health | grep -q "healthy"
    return $?
}

# Функция проверки CORS proxy
check_cors_proxy() {
    curl -s http://localhost:8081/api/censorship/test | grep -q "ok"
    return $?
}

# Функция проверки Cloudflare
check_cloudflare() {
    local url=$1
    if [ -n "$url" ]; then
        curl -s --max-time 5 "$url/api/censorship/test" | grep -q "ok"
        return $?
    fi
    return 1
}

# Проверяем и запускаем бэкенд
if ! check_backend; then
    echo "⚠️  Бэкенд не работает. Запуск..."
    cd /home/c1ten12/music-app/backend
    source venv/bin/activate
    nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
    sleep 3
    if check_backend; then
        echo "✅ Бэкенд запущен"
    else
        echo "❌ Не удалось запустить бэкенд"
        exit 1
    fi
else
    echo "✅ Бэкенд работает (порт 8000)"
fi

# Проверяем и запускаем CORS proxy
if ! check_cors_proxy; then
    echo "⚠️  CORS Proxy не работает. Запуск..."
    cd /home/c1ten12/music-app/backend
    source venv/bin/activate
    nohup python cors_proxy_8081.py > /tmp/cors.log 2>&1 &
    sleep 3
    if check_cors_proxy; then
        echo "✅ CORS Proxy запущен"
    else
        echo "❌ Не удалось запустить CORS Proxy"
        exit 1
    fi
else
    echo "✅ CORS Proxy работает (порт 8081)"
fi

# Получаем текущий URL из musicApi.js
CURRENT_URL=$(grep "const API_URL" /home/c1ten12/music-app/frontend/src/api/musicApi.js | sed "s/.*'\(.*\)'.*/\1/")
echo ""
echo "📡 Текущий API URL: $CURRENT_URL"

# Проверяем работу текущего URL
if check_cloudflare "$CURRENT_URL"; then
    echo "✅ Cloudflare туннель работает"
    echo ""
    echo "===================================================="
    echo "✅ ВСЁ РАБОТАЕТ!"
    echo ""
    echo "🌐 Frontend: https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/"
    echo "🔗 API URL: $CURRENT_URL"
    echo ""
    echo "Проверка связи:"
    echo "  curl $CURRENT_URL/api/censorship/test"
    echo "===================================================="
    exit 0
fi

echo "⚠️  Текущий URL не работает. Перезапуск Cloudflare..."

# Убиваем старый cloudflared
pkill -f cloudflared 2>/dev/null
sleep 2

# Запускаем новый Cloudflare
echo "Запуск Cloudflare Tunnel..."
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 2>&1 | tee /tmp/cf.txt &
sleep 10

# Получаем новый URL
NEW_URL=$(grep "trycloudflare.com" /tmp/cf.txt | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)

if [ -z "$NEW_URL" ]; then
    # Пробуем получить из ps
    NEW_URL=$(ps aux | grep cloudflared | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | head -1)
fi

if [ -z "$NEW_URL" ]; then
    echo "❌ Не удалось получить Cloudflare URL"
    echo "Проверьте: tail -f /tmp/cf.txt"
    exit 1
fi

echo "✅ Новый URL: $NEW_URL"

# Обновляем фронтенд
echo ""
echo "🔄 Обновление фронтенда..."

# Обновляем musicApi.js
sed -i "s|const API_URL = .*|const API_URL = '$NEW_URL/api';|" \
    /home/c1ten12/music-app/frontend/src/api/musicApi.js

# Обновляем Search.jsx
sed -i "s|https://[a-zA-Z0-9.-]*trycloudflare.com|$NEW_URL|g" \
    /home/c1ten12/music-app/frontend/src/pages/Search.jsx

# Собираем фронтенд
cd /home/c1ten12/music-app/frontend
npm run build > /tmp/build.log 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  Ошибка сборки, пробуем продолжить..."
fi

# Коммитим и пушим
cd ..
git add -f frontend/dist frontend/src/api/musicApi.js frontend/src/pages/Search.jsx
git commit -m "Fix connection: $NEW_URL" 2>/dev/null
git push origin main > /tmp/push.log 2>&1

echo "✅ Фронтенд обновлён"

# Финальная проверка
sleep 3
if check_cloudflare "$NEW_URL"; then
    echo ""
    echo "===================================================="
    echo "✅ СВЯЗЬ ВОССТАНОВЛЕНА!"
    echo ""
    echo "🌐 Frontend: https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/"
    echo "🔗 API URL: $NEW_URL"
    echo ""
    echo "📱 GitHub Pages обновится через 1-2 минуты"
    echo ""
    echo "🔧 Команды для проверки:"
    echo "  curl $NEW_URL/api/censorship/test"
    echo "  curl $NEW_URL/health"
    echo "===================================================="
else
    echo ""
    echo "⚠️  Cloudflare работает нестабильно"
    echo "Попробуйте перезапустить: ./fix-connection.sh"
    echo ""
    echo "Текущий URL: $NEW_URL"
fi
