#!/bin/bash
# 🔧 ПОЛНАЯ НАСТРОЙКА СВОЕГО ХОСТИНГА
# Без внешних сервисов - только своё!

set -e

echo "🔧 Настройка собственного хостинга..."
echo "======================================"
echo ""

# 1. Установка Nginx
echo "📦 Установка Nginx..."
sudo apt update -qq
sudo apt install -y nginx > /dev/null 2>&1
echo "✅ Nginx установлен"

# 2. Конфигурация Nginx
echo ""
echo "⚙️  Настройка Nginx..."

sudo cat > /etc/nginx/sites-available/music-app << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Бэкенд API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Subsonic API
    location /rest/ {
        proxy_pass http://localhost:8000/rest/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Фронтенд (статика)
    location / {
        root /home/c1ten12/music-app/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t > /dev/null 2>&1
sudo systemctl restart nginx

echo "✅ Nginx настроен"

# 3. HTTPS через Let's Encrypt
echo ""
echo "🔒 Настройка HTTPS..."
echo ""
echo "⚠️  Для HTTPS нужен ДОМЕН (не субдомен!)"
echo ""
echo "Варианты:"
echo "  1. Купить домен (~$9/год) - ЛУЧШИЙ ВАРИАНТ"
echo "  2. Бесплатный eu.org (1-3 дня ожидание)"
echo "  3. Использовать HTTP по IP (работает сейчас)"
echo ""
read -p "Хотите настроить HTTPS? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Введите ваш домен: " DOMAIN
    
    sudo apt install -y certbot python3-certbot-nginx > /dev/null 2>&1
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email your@email.com
    
    echo "✅ HTTPS настроен для $DOMAIN"
else
    echo ""
    echo "⚠️  Будет работать HTTP"
    echo ""
fi

# 4. Автозапуск сервисов
echo ""
echo "🔄 Настройка автозапуска..."

# Systemd сервисы
if [ -f "/home/c1ten12/music-app/music-app-backend.service" ]; then
    sudo cp /home/c1ten12/music-app/music-app-*.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable music-app-backend
    sudo systemctl enable music-app-cors
    sudo systemctl start music-app-backend
    sudo systemctl start music-app-cors
    echo "✅ Сервисы настроены"
fi

# 5. Итог
echo ""
echo "======================================"
echo "✅ НАСТРОЙКА ЗАВЕРШЕНА!"
echo ""
echo "🌐 Доступ:"

if [ -n "$DOMAIN" ]; then
    echo "   HTTPS: https://$DOMAIN"
    echo "   HTTP:  http://$DOMAIN"
else
    echo "   HTTP:  http://78.140.249.136"
    echo "   API:   http://78.140.249.136:8000"
    echo "   CORS:  http://78.140.249.136:8081"
fi

echo ""
echo "📊 Статус:"
echo "   sudo systemctl status nginx"
echo "   sudo systemctl status music-app-backend"
echo "   sudo systemctl status music-app-cors"
echo ""
echo "📁 Логи:"
echo "   sudo journalctl -u nginx -f"
echo "   sudo journalctl -u music-app-backend -f"
echo ""
echo "======================================"
