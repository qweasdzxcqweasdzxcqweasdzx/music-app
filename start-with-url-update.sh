#!/bin/bash
# Автоматический запуск с обновлением URL

echo "🎵 Music App - Запуск с авто-обновлением URL"
echo "============================================"

# Останавливаем старое
pkill -f cloudflared 2>/dev/null
sleep 2

# Запускаем сервер и CORS proxy если не работают
if ! curl -s http://localhost:8000/health | grep -q healthy; then
    echo "Запуск сервера..."
    cd /home/c1ten12/music-app/backend
    source venv/bin/activate
    nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
    sleep 3
fi

if ! curl -s http://localhost:8081/api/censorship/test | grep -q ok; then
    echo "Запуск CORS Proxy..."
    cd /home/c1ten12/music-app/backend
    source venv/bin/activate
    nohup python cors_proxy_8081.py > /tmp/cors.log 2>&1 &
    sleep 3
fi

# Запускаем Cloudflare
echo "Запуск Cloudflare..."
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 2>&1 | tee /tmp/cf.txt &
sleep 12

# Получаем URL из stdout Cloudflare
URL=$(grep "trycloudflare.com" /tmp/cf.txt | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)

# Если не получилось, пробуем другой способ
if [ -z "$URL" ]; then
    URL=$(ps aux | grep cloudflared | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | head -1)
fi

if [ -n "$URL" ]; then
    echo "✅ Cloudflare запущен"
    echo "🌐 URL: $URL"
    
    # Обновляем фронтенд
    echo "Обновление фронтенда..."
    cd /home/c1ten12/music-app/frontend/src/api
    sed -i "s|const API_URL = .*|const API_URL = '$URL/api';|" musicApi.js
    
    cd ../pages
    sed -i "s|https://[a-zA-Z0-9.-]*trycloudflare.com|$URL|g" Search.jsx
    
    # Собираем
    cd /home/c1ten12/music-app/frontend
    npm run build > /tmp/build.log 2>&1
    
    # Пушим
    cd ..
    git add -f frontend/dist frontend/src/api/musicApi.js frontend/src/pages/Search.jsx
    git commit -m "Auto-update: $URL" 2>/dev/null
    git push origin main > /tmp/push.log 2>&1
    
    echo "✅ Фронтенд обновлён"
    echo ""
    echo "============================================"
    echo "✅ ВСЁ РАБОТАЕТ!"
    echo ""
    echo "🌐 ОТКРОЙТЕ:"
    echo "$URL"
    echo ""
    echo "📱 GitHub Pages (обновится через 1-2 мин):"
    echo "https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/"
    echo "============================================"
else
    echo "❌ Cloudflare не запустился"
    echo "Проверьте логи: tail /tmp/cf.log"
fi
