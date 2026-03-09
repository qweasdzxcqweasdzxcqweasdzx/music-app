#!/bin/bash
# 🌐 Быстрый запуск Cloudflare Tunnel для Telegram

echo "🌐 Запуск Cloudflare Tunnel для Telegram..."
echo ""

# Остановка старого
pkill -f cloudflared 2>/dev/null
sleep 2

# Запуск в screen сессии
screen -dmS cloudflared /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081

echo "⏳ Ожидание подключения (15 сек)..."
sleep 15

# Получение URL
URL=$(cat /tmp/cf*.log 2>/dev/null | grep "trycloudflare.com" | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)

if [ -n "$URL" ]; then
    echo ""
    echo "✅ Cloudflare запущен!"
    echo ""
    echo "🔗 Ваш HTTPS URL:"
    echo "   $URL"
    echo ""
    echo "📱 Используйте в Telegram боте:"
    echo "   @BotFather → /newapp → URL: $URL"
    echo ""
    echo "📊 Проверка:"
    echo "   curl $URL/api/censorship/test"
    echo ""
    echo "🛑 Остановка:"
    echo "   pkill -f cloudflared"
    echo "   или: screen -S cloudflared -X quit"
    echo ""
    
    # Сохранение URL
    echo "$URL" > /tmp/cloudflare_url.txt
    
    # Проверка работы
    echo "🔄 Проверка работы..."
    sleep 3
    if curl -s --max-time 5 "$URL/api/censorship/test" | grep -q "ok"; then
        echo "✅ Всё работает!"
    else
        echo "⚠️  Cloudflare нестабилен (это нормально для Quick Tunnel)"
        echo "   Если не работает - запустите ещё раз: ./start-cloudflare.sh"
    fi
else
    echo "❌ Не удалось получить URL"
    echo "   Проверьте: screen -ls cloudflared"
fi
