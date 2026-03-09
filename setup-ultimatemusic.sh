#!/bin/bash
# 🚀 Настройка для ultimatemusic.c6t.ru

echo "🚀 Настройка ultimatemusic.c6t.ru"
echo "=================================="
echo ""

# Проверка DNS
echo "📊 Проверка DNS..."
if ping -c 1 ultimatemusic.c6t.ru > /dev/null 2>&1; then
    echo "✅ DNS работает"
else
    echo "⚠️  DNS ещё не настроен"
    echo ""
    echo "Добавьте DNS запись у регистратора:"
    echo "  Тип: A"
    echo "  Имя: @"
    echo "  Значение: 78.140.249.136"
    echo ""
    read -p "Продолжить без проверки DNS? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Конфиг Nginx
echo ""
echo "⚙️  Создание конфига Nginx..."

cat > /tmp/music-nginx.conf << 'EOF'
server {
    listen 80;
    server_name ultimatemusic.c6t.ru www.ultimatemusic.c6t.ru;
    
    location / {
        root /home/c1ten12/music-app/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /rest/ {
        proxy_pass http://localhost:8000/rest/;
        proxy_set_header Host $host;
    }
    
    location /static/ {
        proxy_pass http://localhost:8000/static/;
    }
}
EOF

echo "✅ Конфиг создан: /tmp/music-nginx.conf"
echo ""
echo "⚠️  ДЛЯ ПРИМЕНЕНИЯ НУЖЕН SUDO!"
echo ""
echo "Выполните:"
echo "  sudo cp /tmp/music-nginx.conf /etc/nginx/sites-available/music-app"
echo "  sudo ln -sf /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/"
echo "  sudo rm -f /etc/nginx/sites-enabled/default"
echo "  sudo nginx -t"
echo "  sudo systemctl restart nginx"
echo ""

# HTTPS
echo "🔒 Для HTTPS выполните:"
echo "  sudo apt install -y certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d ultimatemusic.c6t.ru -d www.ultimatemusic.c6t.ru"
echo ""

echo "=================================="
echo "✅ ИНСТРУКЦИЯ ГОТОВА!"
echo ""
echo "📖 Полный файл: ULTIMATEMUSIC_SETUP.md"
