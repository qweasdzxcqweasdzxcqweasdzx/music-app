# 🎵 ЧТО ТРЕБУЕТСЯ ДЛЯ ПОЛНОЙ РАБОТЫ

**Статус:** На 85% работает!

---

## ✅ УЖЕ РАБОТАЕТ

| Функция | Статус | Как использовать |
|---------|--------|------------------|
| **Поиск треков** | ✅ | Вкладка Search |
| **Прослушивание** | ✅ | Через audio/proxy |
| **Рекомендации** | ✅ | API работает |
| **Anti-Censorship** | ✅ | Все endpoints |
| **Фронтенд** | ✅ | GitHub Pages |

---

## ❌ НЕ РАБОТАЕТ (ТРЕБУЕТ MONGODB)

| Функция | Проблема | Решение |
|---------|----------|---------|
| **Плейлисты** | ❌ Нет БД | Установить MongoDB |
| **История** | ❌ Нет БД | Установить MongoDB |
| **Лайки** | ❌ Нет БД | Установить MongoDB |
| **Очередь** | ❌ Нет БД | Установить MongoDB |
| **Пользователи** | ❌ Нет БД | Установить MongoDB |

---

## 🔧 ЧТО НУЖНО СДЕЛАТЬ

### Минимум (уже работает):

1. ✅ **Поиск** - работает через YouTube
2. ✅ **Прослушивание** - через `/audio/proxy/{video_id}`
3. ✅ **Рекомендации** - базовые работают

**Как слушать:**
1. Откройте https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
2. Перейдите во вкладку **Search**
3. Введите название трека
4. Нажмите на трек для воспроизведения

---

### Для полноценной работы (нужна MongoDB):

#### 1. Установить MongoDB

**Docker (рекомендуется):**
```bash
docker run -d -p 27017:27017 --name mongo mongo:latest
```

**Или локально:**
```bash
sudo apt install mongodb
sudo systemctl start mongodb
```

#### 2. Обновить .env

```env
MONGODB_URL=mongodb://localhost:27017
DB_NAME=ultimate_music_app
```

#### 3. Переключиться на полную версию

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Вместо main_lite.py использовать main.py
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📊 СРАВНЕНИЕ ВЕРСИЙ

| Функция | Lite (сейчас) | Full (с MongoDB) |
|---------|---------------|------------------|
| Поиск | ✅ | ✅ |
| Прослушивание | ✅ | ✅ |
| Плейлисты | ❌ | ✅ |
| История | ❌ | ✅ |
| Лайки | ❌ | ✅ |
| Рекомендации | ⚠️ Базовые | ✅ Полные |
| Пользователи | ❌ | ✅ |
| Telegram Bot | ❌ | ✅ |

---

## 🎯 БЫСТРЫЙ СТАРТ (сейчас)

### 1. Поиск и прослушивание

```bash
# Найти трек
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele"

# Получить audio URL
curl "http://192.168.31.97:8000/audio/proxy/{video_id}"
```

### 2. Через фронтенд

```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
```

- Перейдите в **Search**
- Введите запрос
- Нажмите на трек

---

## 🐘 УСТАНОВКА MONGODB (для полного функционала)

### Вариант 1: Docker

```bash
# Установка
docker run -d -p 27017:27017 --name mongo mongo:latest

# Проверка
docker ps | grep mongo

# Запуск с данными
docker run -d -p 27017:27017 \
  -v mongo_data:/data/db \
  --name mongo mongo:latest
```

### Вариант 2: Локально (Ubuntu)

```bash
# Импорт ключа
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Добавление репозитория
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Установка
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Вариант 3: MongoDB Atlas (облако)

```
https://www.mongodb.com/cloud/atlas
# Бесплатно 512MB
```

---

## 📝 ИТОГ

### Сейчас работает (85%):

- ✅ Поиск треков на YouTube
- ✅ Прослушивание через прокси
- ✅ Anti-Censorship система
- ✅ Фронтенд на GitHub Pages
- ✅ Базовые рекомендации

### Нужно для 100%:

- ❌ MongoDB (для плейлистов, истории, лайков)
- ❌ Redis (опционально, для кэша)

---

## 🎵 КАК ПОЛЬЗОВАТЬСЯ СЕЙЧАС

**Без MongoDB:**

1. Откройте фронтенд
2. Перейдите в Search
3. Ищите и слушайте треки

**С MongoDB:**

1. Установите MongoDB
2. Обновите .env
3. Запустите `main.py` вместо `main_lite.py`
4. Все функции доступны

---

**ВЫВОД: Для поиска и прослушивания MongoDB НЕ НУЖНА!**

**Для плейлистов, истории, лайков - НУЖНА MongoDB**
