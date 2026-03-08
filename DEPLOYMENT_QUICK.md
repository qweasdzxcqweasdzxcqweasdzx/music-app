# 🚀 ПОЛНОЕ РАЗВЁРТЫВАНИЕ ULTIMATE MUSIC APP

Краткая инструкция для быстрого запуска.

---

## 📋 Чеклист развёртывания

### Бэкенд (сервер)

- [ ] **Шаг 1:** Перейти в директорию бэкенда
  ```bash
  cd /home/c1ten12/music-app/backend
  ```

- [ ] **Шаг 2:** Активировать виртуальное окружение
  ```bash
  source venv/bin/activate
  ```

- [ ] **Шаг 3:** Проверить зависимости
  ```bash
  pip install -r requirements.txt
  pip install yt-dlp
  ```

- [ ] **Шаг 4:** Запустить сервер
  ```bash
  # В фоне
  nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
  
  # Или в foreground
  python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
  ```

- [ ] **Шаг 5:** Проверить сервер
  ```bash
  curl http://localhost:8000/health
  ```

- [ ] **Шаг 6:** Узнать IP сервера
  ```bash
  hostname -I | awk '{print $1}'
  # Запомните этот IP (например: 45.123.67.89)
  ```

---

### Фронтенд (GitHub Pages)

- [ ] **Шаг 1:** Открыть `frontend/src/api/musicApi.js`

- [ ] **Шаг 2:** Изменить API URL на ваш сервер
  ```javascript
  // Было
  const API_URL = 'http://localhost:8000/api';
  
  // Стало (замените IP на ваш)
  const API_URL = 'http://45.123.67.89:8000/api';
  ```

- [ ] **Шаг 3:** Сохранить файл

- [ ] **Шаг 4:** Собрать фронтенд
  ```bash
  cd /home/c1ten12/music-app/frontend
  npm run build
  ```

- [ ] **Шаг 5:** Задеплоить на GitHub
  ```bash
  git add .
  git commit -m "Update API URL and deploy"
  git push
  ```

- [ ] **Шаг 6:** Подождать 1-2 минуты пока GitHub Pages обновится

---

## ✅ Проверка работы

### 1. Откройте Swagger UI

```
http://YOUR_SERVER_IP:8000/docs
```

**Должно открыться:** Swagger UI с документацией API

### 2. Проверьте API

```bash
curl http://YOUR_SERVER_IP:8000/api/censorship/test
```

**Должно вернуть:**
```json
{
  "status": "ok",
  "test": "anti-censorship",
  "results": [...]
}
```

### 3. Откройте фронтенд

```
https://yourusername.github.io/music-app/
```

**Должно открыться:** Приложение

### 4. Проверьте Console (F12)

**Не должно быть:** Ошибок CORS или Network

**Должно быть:** Успешные запросы к `http://YOUR_SERVER_IP:8000/api/...`

---

## 🔧 Если что-то не работает

### Сервер не запускается

```bash
# Проверка логов
cat /tmp/uvicorn.log

# Проверка порта
ss -tlnp | grep 8000

# Перезапуск зависимостей
pip install -r requirements.txt --upgrade
```

### Фронтенд не подключается

1. Проверьте `API_URL` в `musicApi.js`
2. Убедитесь, что сервер доступен:
   ```bash
   curl http://YOUR_SERVER_IP:8000/health
   ```
3. Проверьте CORS в `backend/main_lite.py`:
   ```python
   allow_origins=["*"]
   ```

### Ошибка Mixed Content

**Проблема:** HTTPS фронтенд + HTTP бэкенд

**Решение:** Настройте HTTPS через Nginx:

```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/music-app
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📁 Файлы для настройки

| Файл | Что изменить |
|------|--------------|
| `backend/main_lite.py` | CORS (если нужно) |
| `frontend/src/api/musicApi.js` | API_URL на ваш сервер |
| `frontend/.env` | VITE_API_URL (опционально) |

---

## 🎯 Команды для управления

### Запуск сервера

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

### Остановка сервера

```bash
pkill -f "uvicorn main_lite"
```

### Проверка статуса

```bash
ps aux | grep uvicorn
curl http://localhost:8000/health
```

### Просмотр логов

```bash
tail -f /tmp/uvicorn.log
```

---

## 📊 Архитектура после развёртывания

```
Пользователь
    │
    ▼
https://yourusername.github.io/music-app/
    │ (Frontend - React)
    │ API запросы
    ▼
http://YOUR_SERVER_IP:8000
    │ (Backend - FastAPI)
    ├─ Anti-Censorship System
    ├─ YouTube (yt-dlp)
    └─ SoundCloud API
```

---

## 📞 Поддержка

### Документация

- `backend/DEPLOYMENT.md` - Полный гайд по бэкенду
- `backend/ANTI_CENSORSHIP.md` - Anti-Censorship система
- `frontend/SETUP_API.md` - Настройка фронтенда
- `README.md` - Общая документация

### Тесты

```bash
# Бэкенд тесты
cd backend
python test_blues_simple.py
python test_api_endpoints.py

# Проверка API
curl http://localhost:8000/api/censorship/test
```

---

## ✅ Всё готово!

Ваше приложение работает!

**Фронтенд:** https://yourusername.github.io/music-app/

**Бэкенд:** http://YOUR_SERVER_IP:8000

**Swagger:** http://YOUR_SERVER_IP:8000/docs
