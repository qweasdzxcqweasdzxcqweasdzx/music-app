# 🖥️ Хостинг на втором ПК с Ubuntu

**Полная инструкция по настройке удалённого доступа**

## 📋 Требования

- Второй ПК с Ubuntu 22.04
- Основной ПК (Windows/Mac/Linux)
- Одна локальная сеть (WiFi/Ethernet)

## 🔧 1. Настройка Ubuntu ПК

### 1.1 Проверка проекта

```bash
# Перейдите в проект
cd ~/музыкавтг/backend

# Проверка Python
python3 --version

# Проверка импортов
python3 -c "import fastapi; print('Backend OK')"
```

### 1.2 Настройка .env

```bash
cd ~/музыкавтг/backend
cp .env.example .env
nano .env
```

**Обязательные поля:**
```env
SECRET_KEY=super-secret-key-min-32-characters
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Важно! Разрешить доступ со всей сети
HOST=0.0.0.0
PORT=8000
```

### 1.3 Установка зависимостей

```bash
cd ~/музыкавтг/backend

# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установка
pip install -r requirements.txt

# Фронтенд
cd ../frontend
npm install
```

## 🚀 2. Запуск сервера

### Терминал 1 - Бэкенд

```bash
cd ~/музыкавтг/backend
source venv/bin/activate

# Запуск с доступом по сети
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Терминал 2 - Фронтенд

```bash
cd ~/музыкавтг/frontend

# Обновление API URL
echo "VITE_API_URL=http://$(hostname -I | awk '{print $1}'):8000/api" > .env

# Запуск с доступом по сети
npm run dev -- --host 0.0.0.0
```

**Запомните IP адрес который покажет `hostname -I`**
Пример: `192.168.1.100`

## 🔥 3. Брандмауэр Ubuntu

```bash
# Разрешить порты
sudo ufw allow 5173
sudo ufw allow 8000

# Проверка
sudo ufw status
```

## 💻 4. Доступ с основного ПК

### Вариант A: Локальная сеть

1. **Узнайте IP Ubuntu ПК:**
   ```bash
   # На Ubuntu
   hostname -I
   # Пример: 192.168.1.100
   ```

2. **Откройте на основном ПК:**
   ```
   http://192.168.1.100:5173
   ```

3. **Проверка:**
   ```bash
   # С основного ПК (Windows PowerShell)
   Test-NetConnection 192.168.1.100 -Port 5173
   ```

### Вариант B: Tailscale (рекомендуется)

**Преимущества:**
- ✅ Работает через интернет
- ✅ Безопасно (VPN)
- ✅ Не нужно открывать порты

**На Ubuntu ПК:**
```bash
# Установка
curl -fsSL https://tailscale.com/install.sh | sh

# Запуск
sudo tailscale up

# Скопируйте ссылку из терминала, откройте в браузере
# Войдите через Google/GitHub
```

**На основном ПК:**
```bash
# Windows: скачать с https://tailscale.com/download
# Установить, войти через тот же аккаунт
```

**После подключения:**
1. Откройте Tailscale на любом ПК
2. Найдите IP Ubuntu ПК (вида `100.x.x.x`)
3. Откройте: `http://100.x.x.x:5173`

### Вариант C: Ngrok (быстрый доступ)

**На Ubuntu ПК:**
```bash
# Установка
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok

# Регистрация (получить токен на https://dashboard.ngrok.com)
ngrok config add-authtoken YOUR_TOKEN

# Запуск
ngrok http 5173
```

**Получите URL:** `https://abc123.ngrok.io`

**Откройте на любом ПК в мире!**

### Вариант D: SSH туннель (безопасно)

**С основного ПК:**
```bash
# Windows PowerShell
ssh -L 5173:localhost:5173 -L 8000:8000 user@ubuntu-ip

# После подключения откройте на основном ПК:
http://localhost:5173
```

## 🤖 5. Установка Qwen CLI

**На Ubuntu ПК:**

```bash
# Установка через npm
sudo npm install -g @anthropic-ai/qwen-cli

# Или через pip
pip3 install qwen-cli

# Проверка
qwen --version
```

**Использование в проекте:**
```bash
cd ~/музыкавтг
qwen
```

**На основном ПК:**
```bash
# Windows (PowerShell от администратора)
npm install -g @anthropic-ai/qwen-cli

# Использование
cd музыкавтг
qwen
```

## 🔧 6. Автоматический запуск

### Systemd сервис для бэкенда

```bash
sudo nano /etc/systemd/system/music-backend.service
```

**Содержимое:**
```ini
[Unit]
Description=Music App Backend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/музыкавтг/backend
Environment="PATH=/home/your-username/музыкавтг/backend/venv/bin"
ExecStart=/home/your-username/музыкавтг/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Запуск:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable music-backend
sudo systemctl start music-backend
sudo systemctl status music-backend
```

### PM2 для фронтенда

```bash
# Установка
sudo npm install -g pm2

# Запуск
cd ~/музыкавтг/frontend
pm2 start npm --name "music-frontend" -- run dev -- --host 0.0.0.0

# Автозапуск
pm2 startup
pm2 save
```

## 📊 7. Мониторинг

```bash
# Логи backend
journalctl -u music-backend -f

# Логи frontend
pm2 logs music-frontend

# Статус
pm2 status

# Перезапуск
pm2 restart music-frontend
sudo systemctl restart music-backend
```

## 🐛 8. Troubleshooting

### Не открывается с основного ПК

```bash
# Проверка брандмауэра
sudo ufw status
sudo ufw allow 5173
sudo ufw allow 8000

# Проверка что сервер слушает
netstat -tulpn | grep :5173
netstat -tulpn | grep :8000

# Проверка IP
hostname -I
```

### Tailscale не подключается

```bash
# Переподключение
sudo tailscale logout
sudo tailscale up

# Проверка статуса
tailscale status
```

### ngrok не работает

```bash
# Проверка токена
ngrok config add-authtoken YOUR_TOKEN

# Проверка версии
ngrok --version
```

## 📝 9. Быстрые команды

```bash
# На Ubuntu ПК

# Запуск всего
sudo systemctl start music-backend
pm2 start music-frontend

# Остановка
sudo systemctl stop music-backend
pm2 stop music-frontend

# Перезапуск
sudo systemctl restart music-backend
pm2 restart music-frontend

# Логи
journalctl -u music-backend -f
pm2 logs music-frontend
```

## ✅ 10. Чеклист

- [ ] Проект установлен на Ubuntu ПК
- [ ] .env настроен
- [ ] Зависимости установлены
- [ ] Бэкенд запущен на 0.0.0.0:8000
- [ ] Фронтенд запущен на 0.0.0.0:5173
- [ ] Брандмауэр настроен
- [ ] IP адрес известен
- [ ] Доступ с основного ПК работает
- [ ] Tailscale установлен (опционально)
- [ ] Qwen CLI установлен

---

**Готово! Проект доступен с основного ПК!** 🚀

**IP для доступа:** `http://<ubuntu-pc-ip>:5173`
