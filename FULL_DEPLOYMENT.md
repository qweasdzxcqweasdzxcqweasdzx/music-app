# 🚀 ПОЛНЫЙ ДЕПЛОЙ MUSIC APP НА СЕРВЕРЕ С ДОМЕНОМ

**Дата:** 2026-03-09
**Статус:** ✅ Готово к продакшену

---

## 📋 ЧЕКЛИСТ ТОГО ЧТО НУЖНО

### 1. Домен
- [x] Домен куплен ✅ (у вас уже есть)
- [ ] DNS настроен
- [ ] Домен добавлен в Cloudflare

### 2. Сервер
- [x] Сервер работает ✅ (Linux)
- [x] Проект скачан ✅
- [ ] Python зависимости установлены
- [ ] Node.js зависимости установлены

### 3. Cloudflare
- [ ] Аккаунт Cloudflare создан
- [ ] Домен добавлен в Cloudflare
- [ ] Named Tunnel настроен

### 4. Приложения
- [ ] Бэкенд запущен
- [ ] CORS Proxy запущен
- [ ] Cloudflare Tunnel запущен
- [ ] Systemd сервисы настроены

---

## 🌐 ШАГ 1: НАСТРОЙКА DNS ДЛЯ ДОМЕНА

### Вариант A: Cloudflare Nameservers (РЕКОМЕНДУЕТСЯ)

**1. Зарегистрируйтесь на Cloudflare:**
```
https://dash.cloudflare.com/sign-up
```

**2. Добавьте домен:**
- Click "Add a domain"
- Введите ваш домен (например: `music-app.com`)
- Выберите бесплатный план → Continue

**3. Измените NS серверы у регистратора:**

Cloudflare даст вам 2 NS сервера, например:
```
ns1.cloudflare.com
ns2.cloudflare.com
```

Зайдите к регистратору домена и замените NS серверы на те что дал Cloudflare.

**4. Дождитесь обновления DNS (5-30 минут)**

---

### Вариант B: A-запись (если NS менять нельзя)

Если не можете менять NS серверы, добавьте A-запись:

```
Тип: A
Имя: @ (или music)
Значение: ВАШ_SERVER_IP
TTL: Auto
```

**Узнайте ваш IP:**
```bash
curl ifconfig.me
```

---

## 🔧 ШАГ 2: НАСТРОЙКА CLOUDFLARE NAMED TUNNEL

### 2.1 Создание туннеля

**1. Зайдите в Cloudflare Dashboard:**
```
https://dash.cloudflare.com/
```

**2. Перейдите в Zero Trust:**
```
Zero Trust → Network → Tunnels
```

**3. Создайте туннель:**
- Click "Create a tunnel"
- Имя: `music-app-tunnel`
- Click "Save tunnel"
- Скопируйте токен (длинная строка)

---

### 2.2 Настройка на сервере

**Выполните скрипт:**
```bash
cd /home/c1ten12/music-app
./setup-named-tunnel.sh
```

**Вставьте токен из Cloudflare когда попросит.**

---

### 2.3 Добавьте маршруты в Cloudflare

**В Cloudflare Dashboard:**
```
Zero Trust → Network → Tunnels → music-app-tunnel → Add public hostname
```

**Добавьте 2 записи:**

| Поле | Значение 1 | Значение 2 |
|------|------------|------------|
| **Subdomain** | `api` | `app` |
| **Domain** | `your-domain.com` | `your-domain.com` |
| **Service** | `http://localhost:8081` | `http://localhost:8000` |
| **Type** | `HTTP` | `HTTP` |

**Пример:**
- `api.your-domain.com` → CORS Proxy (порт 8081)
- `app.your-domain.com` → Бэкенд (порт 8000)

---

## 📦 ШАГ 3: УСТАНОВКА ЗАВИСИМОСТЕЙ

### 3.1 Python зависимости

```bash
cd /home/c1ten12/music-app/backend

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Активация и установка
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Node.js зависимости

```bash
cd /home/c1ten12/music-app/frontend

# Установка зависимостей
npm install

# Сборка для продакшена
npm run build
```

---

## 🔧 ШАГ 4: НАСТРОЙКА SYSTEMD СЕРВИСОВ

### 4.1 Установка сервисов

```bash
cd /home/c1ten12/music-app
sudo ./install-systemd.sh
```

**Что сделает скрипт:**
- ✅ Скопирует сервисы в `/etc/systemd/system/`
- ✅ Включит автозапуск
- ✅ Запустит сервисы

---

### 4.2 Проверка сервисов

```bash
# Статус всех сервисов
sudo systemctl status music-app-backend
sudo systemctl status music-app-cors
sudo systemctl status music-app-cloudflared

# Или все сразу
sudo systemctl status music-app-*
```

---

### 4.3 Логи сервисов

```bash
# Бэкенд
sudo journalctl -u music-app-backend -f

# CORS Proxy
sudo journalctl -u music-app-cors -f

# Cloudflare
sudo journalctl -u music-app-cloudflared -f
```

---

## 🔒 ШАГ 5: НАСТРОЙКА ОКРУЖЕНИЯ

### 5.1 Создайте .env файл

```bash
cd /home/c1ten12/music-app/backend
cp .env.example .env
nano .env
```

### 5.2 Заполните .env

```ini
# Server
HOST=0.0.0.0
PORT=8000

# SoundCloud (получите на https://soundcloud.com/you/apps)
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret

# JWT Secret (сгенерируйте случайную строку 32+ символов)
SECRET_KEY=your-super-secret-key-min-32-characters-long

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your_bot_token

# Cloudflare (опционально, для Named Tunnel)
CLOUDFLARE_TUNNEL_ID=your_tunnel_id
```

### 5.3 Перезапустите сервисы

```bash
sudo systemctl restart music-app-backend
```

---

## 🌐 ШАГ 6: НАСТРОЙКА NGINX (ОПЦИОНАЛЬНО)

Если хотите использовать Nginx вместо Cloudflare Tunnel:

### 6.1 Установка Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

### 6.2 Конфигурация Nginx

```bash
sudo nano /etc/nginx/sites-available/music-app
```

**Конфиг:**
```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name app.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.3 Включение конфигурации

```bash
sudo ln -s /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6.4 HTTPS через Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y

sudo certbot --nginx -d api.your-domain.com
sudo certbot --nginx -d app.your-domain.com
```

---

## 📱 ШАГ 7: НАСТРОЙКА TELEGRAM БОТА

### 7.1 Создайте бота

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Введите имя и username
4. Скопируйте токен

### 7.2 Настройте Mini App

1. Отправьте `/newapp`
2. Выберите бота
3. Введите название
4. **URL:** `https://app.your-domain.com`
5. Short name: `music`

### 7.3 Обновите .env

```ini
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 7.4 Перезапустите бэкенд

```bash
sudo systemctl restart music-app-backend
```

---

## 🔍 ШАГ 8: ПРОВЕРКА РАБОТЫ

### 8.1 Проверка DNS

```bash
# Должен показать ваш IP
ping your-domain.com
ping api.your-domain.com
ping app.your-domain.com
```

### 8.2 Проверка Cloudflare Tunnel

```bash
# Статус туннеля
sudo systemctl status music-app-cloudflared

# Логи
sudo journalctl -u music-app-cloudflared -f
```

### 8.3 Проверка endpoints

```bash
# Бэкенд
curl https://app.your-domain.com/health

# CORS Proxy
curl https://api.your-domain.com/api/censorship/test

# Subsonic API
curl "https://app.your-domain.com/rest/ping.view"

# API Keys
curl https://app.your-domain.com/api/keys/public/info
```

### 8.4 Проверка фронтенда

Откройте в браузере:
```
https://app.your-domain.com
```

Или GitHub Pages:
```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
```

---

## 🛠️ УПРАВЛЕНИЕ СЕРВИСАМИ

### Запуск/Остановка/Перезапуск

```bash
# Все сервисы
sudo systemctl start music-app-backend
sudo systemctl start music-app-cors
sudo systemctl start music-app-cloudflared

sudo systemctl stop music-app-backend
sudo systemctl stop music-app-cors
sudo systemctl stop music-app-cloudflared

sudo systemctl restart music-app-backend
sudo systemctl restart music-app-cors
sudo systemctl restart music-app-cloudflared

# Или все сразу
sudo systemctl restart music-app-*
```

### Автозапуск при загрузке

```bash
# Включить (уже включено после install-systemd.sh)
sudo systemctl enable music-app-backend
sudo systemctl enable music-app-cors
sudo systemctl enable music-app-cloudflared

# Проверить
sudo systemctl is-enabled music-app-*
```

---

## 📊 МОНИТОРИНГ

### Логи

```bash
# Все логи music-app
sudo journalctl -u music-app-backend -f
sudo journalctl -u music-app-cors -f
sudo journalctl -u music-app-cloudflared -f

# Последние 100 строк
sudo journalctl -u music-app-backend -n 100
```

### Статус

```bash
# Быстрый статус
cd /home/c1ten12/music-app
./status.sh
```

### Проверка портов

```bash
# Какие порты слушают
sudo ss -tlnp | grep -E '(8000|8081)'

# Или через lsof
sudo lsof -i :8000
sudo lsof -i :8081
```

---

## 🔒 БЕЗОПАСНОСТЬ

### 1. Firewall

```bash
# Разрешить только нужные порты
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Обновления

```bash
# Регулярно обновляйте систему
sudo apt update && sudo apt upgrade -y
```

### 3. Секреты

- ✅ Смените `SECRET_KEY` в .env
- ✅ Не коммитьте .env в git
- ✅ Используйте разные API-ключи для разных клиентов

---

## 📝 DNS ЗАПИСИ - ИТОГ

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| **A** | @ | ВАШ_SERVER_IP | Auto |
| **A** | api | ВАШ_SERVER_IP | Auto |
| **A** | app | ВАШ_SERVER_IP | Auto |
| **NS** | @ | ns1.cloudflare.com | Auto |
| **NS** | @ | ns2.cloudflare.com | Auto |

**Или используйте Cloudflare Nameservers (рекомендуется).**

---

## 🎯 БЫСТРЫЙ СТАРТ (если всё настроено)

```bash
# 1. Проверить зависимости
cd /home/c1ten12/music-app/backend
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
npm run build

# 2. Настроить .env
cd ../backend
nano .env

# 3. Установить сервисы
cd ..
sudo ./install-systemd.sh

# 4. Проверить
./status.sh

# 5. Открыть в браузере
# https://app.your-domain.com
```

---

## 🛠️ TROUBLESHOOTING

### Сервис не запускается

```bash
# Проверить статус
sudo systemctl status music-app-backend

# Посмотреть логи
sudo journalctl -u music-app-backend -n 50

# Перезапустить
sudo systemctl restart music-app-backend
```

### Cloudflare не работает

```bash
# Проверить туннель
sudo systemctl status music-app-cloudflared

# Перезапустить
sudo systemctl restart music-app-cloudflared

# Логи
sudo journalctl -u music-app-cloudflared -f
```

### DNS не обновился

```bash
# Проверить DNS
dig your-domain.com
nslookup your-domain.com

# Очистить кэш (локально)
sudo systemd-resolve --flush-caches
```

### Порт занят

```bash
# Найти процесс
sudo lsof -i :8000

# Убить процесс
sudo kill -9 PID
```

---

## 📞 ПОДДЕРЖКА

### Логи для отладки

```bash
# Собрать все логи
cd /home/c1ten12/music-app
./status.sh > /tmp/status.txt
sudo journalctl -u music-app-backend > /tmp/backend.log
sudo journalctl -u music-app-cors > /tmp/cors.log
sudo journalctl -u music-app-cloudflared > /tmp/cloudflare.log
```

### Команды для проверки

```bash
# Статус
./status.sh

# Проверка связи
./check-connection.sh

# Перезапуск
./stop.sh && ./stable-run.sh
```

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] Домен добавлен в Cloudflare
- [ ] DNS настроен (NS или A записи)
- [ ] Named Tunnel создан
- [ ] Зависимости установлены
- [ ] .env настроен
- [ ] Systemd сервисы установлены
- [ ] Firewall настроен
- [ ] Telegram бот создан
- [ ] Mini App настроен
- [ ] Все endpoints работают

---

**🎵 ГОТОВО! Ваш музыкальный сервер работает!**

Откройте: `https://app.your-domain.com`
