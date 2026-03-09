#!/bin/bash
# Автоматический запуск всех сервисов Music App

echo "🎵 Music App - Автозапуск всех сервисов"
echo "========================================="

# 1. Останавливаем старые процессы
echo ""
echo "1️⃣ Остановка старых процессов..."
pkill -f "uvicorn main_lite" 2>/dev/null
pkill -f "cors_proxy" 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 2

# 2. Запускаем сервер
echo ""
echo "2️⃣ Запуск сервера (порт 8000)..."
cd /home/c1ten12/music-app/backend
source venv/bin/activate
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
sleep 3

if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Сервер работает"
else
    echo "❌ Сервер не запустился"
fi

# 3. Запускаем CORS proxy
echo ""
echo "3️⃣ Запуск CORS Proxy (порт 8081)..."
nohup python cors_proxy_8081.py > /tmp/cors_proxy.log 2>&1 &
sleep 3

if curl -s http://localhost:8081/api/censorship/test | grep -q "ok"; then
    echo "✅ CORS Proxy работает"
else
    echo "❌ CORS Proxy не запустился"
fi

# 4. Запускаем Cloudflare
echo ""
echo "4️⃣ Запуск Cloudflare Tunnel..."
nohup /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 > /tmp/cloudflared.log 2>&1 &
sleep 10

# Получаем URL
CLOUDFLARE_URL=$(grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" /tmp/cloudflared.log | tail -1)

if [ -n "$CLOUDFLARE_URL" ]; then
    echo "✅ Cloudflare работает"
    echo "🌐 HTTPS URL: $CLOUDFLARE_URL"
    
    # Сохраняем URL для фронтенда
    echo "$CLOUDFLARE_URL" > /tmp/cloudflare_url.txt
    
    # Обновляем фронтенд
    echo ""
    echo "5️⃣ Обновление фронтенда..."
    cd /home/c1ten12/music-app/frontend/src/api
    sed -i "s|const API_URL = .*|const API_URL = '$CLOUDFLARE_URL/api';|" musicApi.js
    
    cd ../pages
    sed -i "s|https://[a-zA-Z0-9.-]*trycloudflare.com|$CLOUDFLARE_URL|g" Search.jsx
    
    # Собираем и пушим
    cd /home/c1ten12/music-app/frontend
    npm run build > /tmp/build.log 2>&1
    
    cd ..
    git add -f frontend/dist frontend/src/api/musicApi.js frontend/src/pages/Search.jsx
    git commit -m "Auto-update Cloudflare URL: $CLOUDFLARE_URL"
    git push origin main > /tmp/git.log 2>&1
    
    echo "✅ Фронтенд обновлён"
else
    echo "❌ Cloudflare не запустился"
fi

echo ""
echo "========================================="
echo "✅ ВСЁ ЗАПУЩЕНО!"
echo ""
echo "🌐 ФРОНТЕНД:"
echo "https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/"
echo ""
echo "⏳ Подождите 1-2 минуты пока GitHub обновится"
echo "========================================="

# Показываем статус
echo ""
echo "📊 СТАТУС:"
echo "Сервер: $(curl -s http://localhost:8000/health > /dev/null && echo '✅' || echo '❌')"
echo "CORS Proxy: $(curl -s http://localhost:8081/api/censorship/test > /dev/null && echo '✅' || echo '❌')"
echo "Cloudflare: $(ps aux | grep cloudflared | grep -v grep > /dev/null && echo '✅' || echo '❌')"
