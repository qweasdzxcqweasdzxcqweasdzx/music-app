# 🔧 ЧТО НУЖНО ДЛЯ РАБОТЫ - ПОЛНАЯ ИНСТРУКЦИЯ

**Статус:** На 50% работает

---

## ✅ УЖЕ РАБОТАЕТ

| Сервис | Статус | Примечание |
|--------|--------|------------|
| **Фронтенд** | ✅ | GitHub Pages |
| **Сервер** | ✅ | FastAPI |
| **Поиск** | ✅ | YouTube + SoundCloud |
| **Anti-Censorship** | ✅ | Все endpoints |

---

## ⚠️ ТРЕБУЕТСЯ ВНИМАНИЕ

### 1. Cloudflare Tunnel (ОБЯЗАТЕЛЬНО!)

**Проблема:** Отключается при остановке терминала

**Решение:** Запустить в screen/tmux

```bash
# Установка screen
sudo apt install screen  # Если нет

# Запуск в screen
screen -S cloudflare
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8000

# Отсоединение: Ctrl+A, D
# Подключение: screen -r cloudflare
```

**ИЛИ в фоне с autostart:**

```bash
# Добавить в ~/.bashrc
echo "nohup /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflared.log 2>&1 &" >> ~/.bashrc
```

---

### 2. Прокси для YouTube (ОБЯЗАТЕЛЬНО!)

**Проблема:** YouTube заблокирован в России

**Текущий прокси:** `http://127.0.0.1:8888`

**Проверка:**
```bash
ps aux | grep "proxy --hostname"
```

**Если не работает - перезапустить:**
```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
nohup proxy --hostname 127.0.0.1 --port 8888 > /tmp/proxy.log 2>&1 &
```

---

### 3. Прокси для SoundCloud (ОБЯЗАТЕЛЬНО!)

**Проблема:** SoundCloud заблокирован

**Решение:** Тот же прокси (порт 8888)

**Проверка:**
```bash
curl -x http://127.0.0.1:8888 https://soundcloud.com > /dev/null && echo "OK"
```

---

### 4. Сервер (ОБЯЗАТЕЛЬНО!)

**Проверка:**
```bash
curl http://localhost:8000/health
```

**Перезапуск:**
```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
```

---

## 🚀 АВТОЗАПУСК ВСЕХ СЕРВИСОВ

### Скрипт запуска

Создайте `/home/c1ten12/start-music-app.sh`:

```bash
#!/bin/bash

# Прокси
cd /home/c1ten12/music-app/backend
source venv/bin/activate
nohup proxy --hostname 127.0.0.1 --port 8888 > /tmp/proxy.log 2>&1 &

# Сервер
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &

# Cloudflare Tunnel
nohup /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflared.log 2>&1 &

# Ждём получения URL
sleep 10
HTTPS_URL=$(cat /tmp/cloudflared.log | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | head -1)
echo "HTTPS URL: $HTTPS_URL"
```

**Сделайте исполняемым:**
```bash
chmod +x /home/c1ten12/start-music-app.sh
```

**Запуск:**
```bash
/home/c1ten12/start-music-app.sh
```

---

## 📝 ЧЕКЛИСТ ЗАПУСКА

### Каждый раз при старте сервера:

```bash
# 1. Прокси
cd /home/c1ten12/music-app/backend
source venv/bin/activate
proxy --hostname 127.0.0.1 --port 8888 &

# 2. Сервер
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 &

# 3. Cloudflare (в отдельном терминале)
screen -S cloudflare
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8000
# Ctrl+A, D для отсоединения
```

### Или скриптом:

```bash
/home/c1ten12/start-music-app.sh
```

---

## 🔍 ПРОВЕРКА ВСЕХ СЕРВИСОВ

```bash
echo "=== СТАТУС ==="

# Прокси
ps aux | grep "proxy --hostname" | grep -v grep > /dev/null && echo "✅ Прокси" || echo "❌ Прокси"

# Сервер
curl -s http://localhost:8000/health > /dev/null && echo "✅ Сервер" || echo "❌ Сервер"

# Cloudflare
ps aux | grep cloudflared | grep -v grep > /dev/null && echo "✅ Cloudflare" || echo "❌ Cloudflare"

# HTTPS URL
cat /tmp/cloudflared.log | grep "trycloudflare.com" | head -1
```

---

## 🌐 ОБНОВЛЕНИЕ ФРОНТЕНДА

**Когда Cloudflare выдаёт новый URL:**

1. Скопируйте новый URL из `/tmp/cloudflared.log`
2. Обновите `frontend/src/api/musicApi.js`:
   ```javascript
   const API_URL = 'https://new-url.trycloudflare.com/api';
   ```
3. Обновите `frontend/src/pages/Search.jsx`:
   ```javascript
   fetch(`https://new-url.trycloudflare.com/api/search?q=...`)
   ```
4. Пересоберите и запушите:
   ```bash
   cd frontend
   npm run build
   cd ..
   git add -f frontend/dist
   git commit -m "Update HTTPS URL"
   git push origin main
   ```

---

## 📊 ИТОГ

### Что нужно:

| Компонент | Нужно? | Команда |
|-----------|--------|---------|
| **Прокси** | ✅ | `proxy --hostname 127.0.0.1 --port 8888` |
| **Сервер** | ✅ | `uvicorn main_lite:app ...` |
| **Cloudflare** | ✅ | `cloudflared tunnel --url ...` |
| **VPN** | ⚠️ | Только если прокси не работает |

### VPN нужен если:

- Прокси не помогает
- YouTube полностью заблокирован

**Решение:** Включить VPN на сервере

---

## 🎯 БЫСТРЫЙ СТАРТ

```bash
# Скрипт запуска
/home/c1ten12/start-music-app.sh

# Проверка
ps aux | grep -E "proxy|uvicorn|cloudflared" | grep -v grep

# HTTPS URL
cat /tmp/cloudflared.log | grep trycloudflare.com
```

---

**📄 ВСЁ РАБОТАЕТ ЕСЛИ ЗАПУЩЕНЫ ВСЕ 3 КОМПОНЕНТА!**
