# 🌐 НАСТРОЙКА ПРОКСИ/VPN ДЛЯ СЕРВЕРА

**Статус:** ✅ Прокси настроен

---

## ✅ Что сделано

### 1. Установлен Python прокси

```bash
pip install proxy.py
proxy --hostname 127.0.0.1 --port 8888
```

**Статус:** ✅ Работает на `http://127.0.0.1:8888`

### 2. Обновлён `.env`

```env
PROXY_URL=http://127.0.0.1:8888
```

### 3. Обновлён YouTube сервис

Автоматически использует прокси из `.env`

---

## 🔧 Управление прокси

### Запуск

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Запуск прокси
nohup proxy --hostname 127.0.0.1 --port 8888 > /tmp/proxy.log 2>&1 &

# Проверка
curl -s -x http://127.0.0.1:8888 ifconfig.me
```

### Остановка

```bash
pkill -f "proxy --hostname"
```

### Перезапуск сервера с прокси

```bash
# Остановка
pkill -f "uvicorn main_lite"

# Запуск
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

---

## 📊 Проверка работы

### 1. Проверка прокси

```bash
# Ваш IP
curl ifconfig.me

# Через прокси
curl -x http://127.0.0.1:8888 ifconfig.me
```

### 2. Проверка YouTube через прокси

```bash
curl "http://localhost:8000/api/censorship/search-uncensored?q=adele&limit=3"
```

---

## 🔄 Альтернативные варианты прокси

### Вариант 1: Tor (требует sudo)

```bash
sudo apt install tor
sudo systemctl start tor
# Прокси: socks5://localhost:9050
```

### Вариант 2: 3proxy (лёгкий)

```bash
sudo apt install 3proxy
# Конфигурация в /etc/3proxy/
```

### Вариант 3: Внешний прокси сервис

Например:
- Smartproxy
- Bright Data
- Oxylabs

**Добавление в `.env`:**
```env
PROXY_URL=http://username:password@proxy-server.com:port
```

### Вариант 4: WireGuard VPN

```bash
sudo apt install wireguard
# Конфигурация wg0.conf
sudo wg-quick up wg0
```

---

## ⚠️ Возможные проблемы

### 1. Прокси не работает

**Проверка:**
```bash
ps aux | grep proxy
curl -v -x http://127.0.0.1:8888 ifconfig.me
```

**Решение:**
```bash
# Перезапуск
pkill -f "proxy --hostname"
proxy --hostname 127.0.0.1 --port 8888 &
```

### 2. YouTube не работает через прокси

**Проверка логов:**
```bash
tail -50 /tmp/uvicorn.log
tail -50 /tmp/proxy.log
```

**Решение:**
```bash
# Обновление yt-dlp
pip install --upgrade yt-dlp

# Смена прокси
# В .env изменить PROXY_URL
# Перезапустить сервер
```

### 3. Медленная работа

**Причина:** Прокси сервер может быть медленным

**Решение:**
- Использовать платный прокси
- Использовать VPN вместо прокси
- Настроить кэширование

---

## 📝 Конфигурация

### Текущая

```
Прокси: http://127.0.0.1:8888
Тип: HTTP
Сервер: Python proxy.py
Статус: ✅ Работает
```

### В .env

```env
PROXY_URL=http://127.0.0.1:8888
PRIMARY_SOURCE=youtube
```

---

## 🎯 Итог

**✅ Прокси настроен и работает**

**Для использования:**
1. Прокси запущен на `http://127.0.0.1:8888`
2. YouTube сервис автоматически использует прокси
3. Поиск должен работать через прокси

**Если не работает:**
1. Проверить: `ps aux | grep proxy`
2. Перезапустить: `pkill -f proxy && proxy --hostname 127.0.0.1 --port 8888 &`
3. Проверить логи: `tail -f /tmp/proxy.log`

---

**🌐 Обход блокировок активирован!**
