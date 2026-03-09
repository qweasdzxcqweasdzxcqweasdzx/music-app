#!/bin/bash
# 🔄 Скрипт проверки и авто-перезапуска Cloudflare

LOG="/tmp/cf-auto-restart.log"
PID_FILE="/tmp/cftunnel.pid"
URL_FILE="/tmp/cloudflare_url.txt"

# Функция проверки работы URL
check_url() {
    local url=$1
    if curl -s --max-time 5 "$url/api/censorship/test" 2>/dev/null | grep -q "ok"; then
        return 0
    fi
    return 1
}

# Проверяем работает ли cloudflared
if ! screen -ls | grep -q "cftunnel"; then
    echo "$(date): ❌ Cloudflare не найден, запускаем..." >> $LOG
    
    # Запуск в screen
    screen -dmS cftunnel /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081
    echo $! > $PID_FILE
    
    sleep 15
    
    # Получаем URL
    NEW_URL=$(cat /tmp/cf.log 2>/dev/null | grep "trycloudflare.com" | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)
    
    if [ -n "$NEW_URL" ]; then
        echo "$NEW_URL" > $URL_FILE
        echo "$(date): ✅ Запущен: $NEW_URL" >> $LOG
    else
        echo "$(date): ⚠️ Не удалось получить URL" >> $LOG
    fi
else
    # Проверяем работает ли текущий URL
    CURRENT_URL=$(cat $URL_FILE 2>/dev/null)
    
    if [ -n "$CURRENT_URL" ]; then
        if ! check_url "$CURRENT_URL"; then
            echo "$(date): ⚠️ URL не работает, перезапуск..." >> $LOG
            
            # Остановка
            screen -S cftunnel -X quit 2>/dev/null
            sleep 2
            
            # Запуск
            screen -dmS cftunnel /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081
            sleep 15
            
            # Новый URL
            NEW_URL=$(cat /tmp/cf.log 2>/dev/null | grep "trycloudflare.com" | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1)
            
            if [ -n "$NEW_URL" ]; then
                echo "$NEW_URL" > $URL_FILE
                echo "$(date): ✅ Перезапущен: $NEW_URL" >> $LOG
            fi
        fi
    fi
fi
