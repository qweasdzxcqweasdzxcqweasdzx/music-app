#!/bin/bash
# 🔄 Авто-перезапуск Cloudflare Tunnel для стабильности

LOG_FILE="/tmp/cloudflared-monitor.log"
PID_FILE="/tmp/cloudflared.pid"
URL_FILE="/tmp/cloudflare_url.txt"

echo "🔄 Монитор Cloudflare Tunnel запущен" | tee -a $LOG_FILE

while true; do
    # Проверка работает ли cloudflared
    if ! pgrep -f "cloudflared tunnel" > /dev/null; then
        echo "$(date): ⚠️ Cloudflare не работает, перезапуск..." | tee -a $LOG_FILE
        
        # Запуск
        /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 > /tmp/cf.log 2>&1 &
        CF_PID=$!
        echo $CF_PID > $PID_FILE
        
        echo "$(date): ✅ Cloudflare запущен (PID: $CF_PID)" | tee -a $LOG_FILE
        
        # Ждём получения URL
        sleep 15
        
        # Получаем URL
        NEW_URL=$(grep "trycloudflare.com" /tmp/cf.log | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)
        
        if [ -n "$NEW_URL" ]; then
            echo "$NEW_URL" > $URL_FILE
            echo "$(date): 🌐 Новый URL: $NEW_URL" | tee -a $LOG_FILE
        fi
    fi
    
    # Проверка каждые 30 секунд
    sleep 30
done
