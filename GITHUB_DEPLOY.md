# 🚀 Инструкция по деплою на GitHub

## ✅ Выполнено

- [x] Git репозиторий инициализирован
- [x] Все файлы добавлены и закоммичены
- [x] Создан коммит с подробным описанием изменений

---

## 📤 Пуш на GitHub

### Вариант 1: Создать новый репозиторий

1. **Создайте репозиторий на GitHub:**
   - Перейдите на https://github.com/new
   - Repository name: `music-app` (или другое название)
   - Description: "🎵 Ultimate Music App v3.0 - SoundCloud + Telegram Mini App"
   - Public или Private (на ваш выбор)
   - **НЕ** ставьте галочки на "Initialize this repository with..."
   - Нажмите "Create repository"

2. **Выполните команды:**
   ```bash
   cd /home/c1ten12/music-app
   
   # Добавьте remote (замените USERNAME на ваш username GitHub)
   git remote add origin https://github.com/USERNAME/music-app.git
   
   # Или через SSH (если настроен)
   git remote add origin git@github.com:USERNAME/music-app.git
   
   # Проверьте remote
   git remote -v
   
   # Сделайте пуш
   git push -u origin main
   ```

### Вариант 2: Если репозиторий уже существует

```bash
cd /home/c1ten12/music-app

# Добавьте remote
git remote add origin https://github.com/USERNAME/EXISTING_REPO.git

# Переименуйте ветку если нужно
git branch -M main

# Сделайте пуш с force (если есть конфликты)
git push -u --force origin main
```

---

## 🔐 Аутентификация на GitHub

### Через HTTPS (рекомендуется)

При пуше GitHub запросит логин и пароль.
**Вместо пароля используйте Personal Access Token:**

1. Перейдите на https://github.com/settings/tokens
2. Нажмите "Generate new token (classic)"
3. Выберите scope: `repo` (полный доступ к репозиториям)
4. Скопируйте токен
5. При пуше используйте токен вместо пароля

### Через SSH

```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your_email@example.com"

# Добавление ключа в агент
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Копирование публичного ключа
cat ~/.ssh/id_ed25519.pub

# Добавьте ключ на GitHub:
# https://github.com/settings/keys
```

---

## 📊 Статистика коммита

```
69 files changed, 17981 insertions(+)

Основные файлы:
- backend/services/censorship_service.py (611 строк)
- backend/services/music_service.py (429 строк)
- frontend/src/components/TabBar.jsx (85 строк)
- frontend/src/api/musicApi.js (511 строк)
- backend/tests/test_censorship.py (280+ строк)
- backend/CENSORSHIP_v2.md (350+ строк)
- frontend/TELEGRAM_SETUP.md (200+ строк)
```

---

## 🌐 GitHub Pages (для фронтенда)

Если хотите разместить фронтенд на GitHub Pages:

1. **Включите GitHub Pages:**
   - Settings → Pages
   - Source: GitHub Actions
   - Или выберите ветку `main` и папку `/frontend/dist`

2. **Настройте workflow:**
   ```bash
   # В frontend/.github/workflows уже есть deploy.yml
   # Просто запушьте изменения
   git push origin main
   ```

3. **URL приложения:**
   ```
   https://USERNAME.github.io/music-app/
   ```

---

## 📱 Настройка Telegram Mini App

После пуша на GitHub:

1. **Соберите фронтенд:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Задеплойте на хостинг:**
   - GitHub Pages
   - Vercel: `vercel deploy`
   - Netlify: `netlify deploy`

3. **В @BotFather:**
   - `/newapp` → создайте Mini App
   - Укажите URL вашего приложения
   - Готово!

---

## 🔄 Последующие коммиты

```bash
# Проверка изменений
git status

# Добавление файлов
git add .

# Коммит
git commit -m "Описание изменений"

# Пуш
git push origin main
```

---

## ⚠️ Важные замечания

### .env файлы
Файлы `.env` добавлены в `.gitignore` и **не будут** запушены.
Для продакшена настройте переменные окружения на сервере.

### node_modules и venv
Папки с зависимостями не добавляются в git.
Устанавливайте зависимости отдельно:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Большие файлы
Если есть большие файлы (>100MB), используйте Git LFS:
```bash
git lfs install
git lfs track "*.mp3"
git lfs track "*.zip"
```

---

## 🎯 Чеклист после пуша

- [ ] Репозиторий создан на GitHub
- [ ] Пуш выполнен успешно
- [ ] GitHub Pages настроен (опционально)
- [ ] Telegram Mini App URL обновлён
- [ ] Переменные окружения настроены на сервере
- [ ] Тесты проходят: `pytest tests/test_censorship.py -v`

---

**Готово!** 🎉

Ваш проект теперь на GitHub с полной историей изменений.
