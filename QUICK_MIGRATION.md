# 🚀 БЫСТРЫЙ ПЕРЕНОС ПРОЕКТА

**Краткая инструкция для переноса Ultimate Music App на другой ПК**

---

## 📦 НА СТАРОМ ПК

### Быстрая подготовка (5 минут)

```bash
cd /home/c1ten12/music-app

# 1. Закоммитьте все изменения
git add .
git commit -m "Before migration"
git push origin main

# 2. Запустите скрипт подготовки
./prepare-migration.sh

# 3. Скопируйте папку migration_backup на новый ПК
#    (через USB, scp, rsync, облако)
```

**Что будет сохранено:**
- ✅ `.env` файлы (backend + frontend)
- ✅ База данных MongoDB (опционально)
- ✅ Музыкальная библиотека (опционально)
- ✅ Информация о системе

---

## 💻 НА НОВОМ ПК

### Быстрая настройка (10 минут)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app.git
cd music-app

# 2. Скопируйте бэкап
cp -r /путь/к/migration_backup ./migration_backup

# 3. Запустите скрипт настройки
./setup-on-new-pc.sh
```

### Ручной запуск

```bash
# Терминал 1 - Backend
cd backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000

# Терминал 2 - CORS Proxy
cd backend
source venv/bin/activate
python cors_proxy_8081.py

# Терминал 3 - Cloudflare (HTTPS)
cloudflared tunnel --url http://localhost:8081

# Терминал 4 - Frontend (разработка)
cd frontend
npm run dev
```

### Проверка

```bash
# Health check
curl http://localhost:8000/health

# API test
curl http://localhost:8081/api/censorship/test
```

---

## 📋 ЧЕКЛИСТ

### На старом ПК:
- [ ] `git push origin main`
- [ ] Запустить `./prepare-migration.sh`
- [ ] Скопировать `migration_backup/` на новый ПК

### На новом ПК:
- [ ] Установить Python 3.9+
- [ ] Установить Node.js 18+
- [ ] Установить MongoDB
- [ ] Установить Redis (опционально)
- [ ] `git clone ...`
- [ ] Скопировать `migration_backup/`
- [ ] Запустить `./setup-on-new-pc.sh`
- [ ] Проверить `curl http://localhost:8000/health`

---

## 🔗 ССЫЛКИ

| Файл | Описание |
|------|----------|
| `MIGRATION_GUIDE.md` | 📖 Полное руководство (30+ шагов) |
| `prepare-migration.sh` | 📦 Скрипт подготовки на старом ПК |
| `setup-on-new-pc.sh` | 🔧 Скрипт настройки на новом ПК |
| `migration_backup/` | 💾 Папка с бэкапами |

---

## ⚡ ЕСЛИ НУЖНО ОЧЕНЬ БЫСТРО

**Минимальный перенос (только код):**

```bash
# Старый ПК
cd /home/c1ten12/music-app
git add . && git commit -m "migration" && git push

# Новый ПК
git clone https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app.git
cd music-app/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install

# Запуск
cd ../backend && python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

**Важно:** Не забудьте вручную создать `.env` файлы!

---

## 🆘 ПОМОЩЬ

**Документация:**
- `MIGRATION_GUIDE.md` - подробная инструкция
- `backend/README.md` - backend
- `frontend/README.md` - frontend

**Логи:**
```bash
tail -f /tmp/server.log    # Backend
tail -f /tmp/cors.log      # CORS Proxy
```

**Проверка:**
```bash
# Порты
ss -tlnp | grep -E '8000|8081'

# Сервисы
sudo systemctl status mongod
sudo systemctl status redis
```

---

**🎵 УДАЧНОГО ПЕРЕНOSА!**
