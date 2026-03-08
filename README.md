# 🎵 Ultimate Music App v3.1

**Музыкальная платформа с Anti-Censorship системой**

![Version](https://img.shields.io/badge/version-3.1.0-blue)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-19-blue)

---

## 🌟 Возможности

### 🔥 Anti-Censorship Система

- **Распознавание цензуры** - автоматическое определение clean/radio версий
- **Поиск оригиналов** - поиск explicit версий на YouTube, SoundCloud
- **Fuzzy Matching** - нахождение треков с отличающимися названиями
- **Мульти-платформенность** - поиск на разных площадках одновременно

### 🎵 Музыкальные источники

| Источник | Статус | Описание |
|----------|--------|----------|
| **SoundCloud** | ✅ | Независимые артисты, ремиксы |
| **YouTube** | ✅ | Оригинал версии через yt-dlp |
| **VK Music** | ⚠️ | Резервный источник |
| **Navidrome** | ⚠️ | Личная коллекция (Subsonic) |

### 🤖 AI Сервисы

- **Suno AI** - генерация песен
- **Mubert** - фоновая музыка
- **LALAL.AI** - разделение на стемы
- **ElevenLabs** - синтез речи

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Pages (Frontend)                    │
│  https://yourusername.github.io/music-app/             │
│  React 19 + Vite                                        │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS API
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Ваш сервер (Backend)                          │
│  http://YOUR_SERVER_IP:8000                            │
│  FastAPI + Anti-Censorship System                       │
│  ├─ Blues Detection Service                            │
│  ├─ YouTube (yt-dlp)                                   │
│  └─ SoundCloud API                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт

### Бэкенд

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

**Проверка:**
```bash
curl http://localhost:8000/health
```

### Фронтенд

1. Откройте `frontend/src/api/musicApi.js`
2. Измените `API_URL` на ваш сервер:
   ```javascript
   const API_URL = 'http://YOUR_SERVER_IP:8000/api';
   ```
3. Соберите и задеплойте:
   ```bash
   npm run build
   npm run deploy
   ```

---

## 📁 Структура проекта

```
music-app/
├── backend/
│   ├── services/
│   │   ├── blues_detection_service.py  # Anti-Censorship ядро
│   │   ├── youtube_service.py          # YouTube поиск
│   │   ├── soundcloud_service.py       # SoundCloud API
│   │   └── ...
│   ├── main_lite.py                    # Сервер (lite)
│   ├── main.py                         # Сервер (full)
│   ├── routes_lite.py                  # API endpoints
│   ├── models.py                       # Pydantic модели
│   ├── config.py                       # Конфигурация
│   ├── requirements.txt                # Зависимости
│   ├── DEPLOYMENT.md                   # Документация по деплою
│   ├── ANTI_CENSORSHIP.md              # Anti-Censorship docs
│   ├── QUICK_START.md                  # Быстрый старт
│   └── test_*.py                       # Тесты
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── musicApi.js             # API клиент (изменить URL!)
│   │   ├── components/
│   │   │   ├── Player.jsx
│   │   │   ├── TrackCard.jsx
│   │   │   └── ...
│   │   └── pages/
│   │       ├── Home.jsx
│   │       ├── Search.jsx
│   │       └── ...
│   ├── package.json
│   ├── vite.config.js
│   └── DEPLOY.md                       # Фронтенд документация
│
├── README.md                           # Этот файл
└── .gitignore
```

---

## 📡 API Endpoints

### Anti-Censorship

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/censorship/check` | GET | Проверка трека на цензуру |
| `/api/censorship/find-original` | POST | Поиск оригинальной версии |
| `/api/censorship/search-uncensored` | GET | Поиск с приоритетом explicit |
| `/api/censorship/analyze-batch` | POST | Массовый анализ треков |
| `/api/censorship/statistics` | GET | Статистика цензуры |
| `/api/censorship/replace-censored` | POST | Замена в плейлистах |
| `/api/censorship/test` | GET | Тест системы |

### Примеры

**Проверка трека:**
```bash
curl "http://YOUR_SERVER_IP:8000/api/censorship/check?track_id=123"
```

**Поиск оригинала:**
```bash
curl -X POST "http://YOUR_SERVER_IP:8000/api/censorship/find-original" \
  -H "Content-Type: application/json" \
  -d '{"track_id": "123"}'
```

**Swagger UI:** http://YOUR_SERVER_IP:8000/docs

---

## 🔧 Настройка

### Бэкенд (.env)

```env
# Server
HOST=0.0.0.0
PORT=8000

# SoundCloud
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret

# JWT
SECRET_KEY=your-secret-key-min-32-chars
```

### Фронтенд (musicApi.js)

```javascript
const API_URL = 'http://YOUR_SERVER_IP:8000/api';
```

---

## 📖 Документация

| Файл | Описание |
|------|----------|
| `backend/DEPLOYMENT.md` | Полное руководство по деплою бэкенда |
| `backend/ANTI_CENSORSHIP.md` | Anti-Censorship система |
| `backend/QUICK_START.md` | Быстрый старт бэкенда |
| `frontend/DEPLOY.md` | Деплой фронтенда |

---

## 🧪 Тесты

### Бэкенд

```bash
cd backend
source venv/bin/activate

# Юнит-тесты
python test_blues_simple.py

# API тесты
python test_api_endpoints.py
```

### Проверка сервера

```bash
# Health check
curl http://localhost:8000/health

# Anti-Censorship тест
curl http://localhost:8000/api/censorship/test
```

---

## 🐘 Production режим

### Systemd сервис

```ini
# /etc/systemd/system/music-app.service
[Unit]
Description=Ultimate Music App Backend
After=network.target

[Service]
User=c1ten12
WorkingDirectory=/home/c1ten12/music-app/backend
Environment="PATH=/home/c1ten12/music-app/backend/venv/bin"
ExecStart=/home/c1ten12/music-app/backend/venv/bin/python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable music-app
sudo systemctl start music-app
sudo systemctl status music-app
```

### HTTPS через Nginx

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

## 📊 Мониторинг

```bash
# Логи
tail -f /tmp/uvicorn.log

# Процесс
ps aux | grep uvicorn

# Порт
ss -tlnp | grep 8000

# Health
curl http://localhost:8000/health
```

---

## 🛠️ Troubleshooting

### Сервер не запускается

```bash
# Проверка логов
cat /tmp/uvicorn.log

# Проверка зависимостей
source venv/bin/activate
pip install -r requirements.txt
```

### CORS ошибки

Убедитесь, что в `main_lite.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Фронтенд не подключается

Проверьте `API_URL` в `frontend/src/api/musicApi.js`

---

## 📈 Производительность

### Оптимизация

- **Gunicorn workers:** `gunicorn main_lite:app -w 4 -k uvicorn.workers.UvicornWorker`
- **Redis кэширование:** (опционально)
- **Rate Limiting:** 60 req/min, 1000 req/hour

---

## 🔒 Безопасность

1. **Firewall:** `sudo ufw allow 8000/tcp`
2. **HTTPS:** Nginx + Let's Encrypt
3. **SECRET_KEY:** Смените на случайную строку
4. **CORS:** Укажите конкретные домены в продакшене

---

## 📝 Changelog

### v3.1.0 (2026)
- ✅ Anti-Censorship System
- ✅ Blues Detection Service
- ✅ Fuzzy Matching
- ✅ YouTube поиск оригиналов
- ✅ Мульти-платформенный поиск
- ✅ 6 новых API endpoints

### v3.0.0
- Multi-source integration
- AI generation
- Smart Mixer

---

## 👨‍💻 Разработчики

- Backend: FastAPI + Python
- Frontend: React 19 + Vite
- Deploy: GitHub Pages + VPS

---

## 📄 License

MIT License

---

**🔗 Ссылки:**
- Frontend: https://yourusername.github.io/music-app/
- Backend API: http://YOUR_SERVER_IP:8000
- Swagger Docs: http://YOUR_SERVER_IP:8000/docs
