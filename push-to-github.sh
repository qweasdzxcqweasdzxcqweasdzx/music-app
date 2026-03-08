#!/bin/bash

# ===========================================
# Скрипт для пуша изменений на GitHub
# ===========================================

set -e

echo "🚀 Ultimate Music App - Push to GitHub"
echo "======================================="
echo ""

# Проверка git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите git."
    exit 1
fi

# Переход в директорию проекта
cd "$(dirname "$0")"

# Проверка что мы в репозитории
if [ ! -d ".git" ]; then
    echo "❌ Это не git репозиторий"
    exit 1
fi

# Получение имени пользователя GitHub
echo ""
echo "📝 Введите ваше имя пользователя GitHub:"
read -r GITHUB_USERNAME

# Получение названия репозитория
echo ""
echo "📁 Введите название репозитория (music-app):"
read -r REPO_NAME
REPO_NAME=${REPO_NAME:-music-app}

# Проверка типа аутентификации
echo ""
echo "🔐 Выберите тип аутентификации:"
echo "1) HTTPS"
echo "2) SSH"
read -r AUTH_TYPE

if [ "$AUTH_TYPE" = "1" ]; then
    REMOTE_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
elif [ "$AUTH_TYPE" = "2" ]; then
    REMOTE_URL="git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
else
    echo "❌ Неверный тип аутентификации"
    exit 1
fi

echo ""
echo "📡 Remote URL: $REMOTE_URL"
echo ""

# Проверка существующих remote
if git remote | grep -q "^origin$"; then
    echo "⚠️  Remote 'origin' уже существует"
    echo "   Хотите перезаписать? (y/n)"
    read -r OVERWRITE
    if [ "$OVERWRITE" = "y" ]; then
        git remote remove origin
    else
        echo "❌ Отмена"
        exit 1
    fi
fi

# Добавление remote
echo "➕ Добавление remote 'origin'..."
git remote add origin "$REMOTE_URL"
echo "✅ Remote добавлен"

# Проверка наличия репозитория на GitHub
echo ""
echo "🔍 Проверка существования репозитория..."
if git ls-remote "$REMOTE_URL" &> /dev/null; then
    echo "✅ Репозиторий существует на GitHub"
    CREATE_REPO="n"
else
    echo "⚠️  Репозиторий не найден на GitHub"
    echo ""
    echo "📝 Хотите создать репозиторий через GitHub CLI? (y/n)"
    echo "   (Требуется установленный gh и авторизация)"
    read -r CREATE_REPO
fi

# Создание репозитория если нужно
if [ "$CREATE_REPO" = "y" ]; then
    if command -v gh &> /dev/null; then
        echo "📦 Создание репозитория..."
        gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    else
        echo ""
        echo "❓ GitHub CLI не установлен."
        echo ""
        echo "📝 Создайте репозиторий вручную:"
        echo "   1. Перейдите на https://github.com/new"
        echo "   2. Repository name: $REPO_NAME"
        echo "   3. Не инициализируйте репозиторий"
        echo "   4. Нажмите 'Create repository'"
        echo ""
        echo "Нажмите Enter когда создадите..."
        read -r
    fi
fi

# Пуш
echo ""
echo "📤 Пуш на GitHub..."
echo "   Ветка: main"
echo "   Remote: origin"
echo ""

# Проверка наличия изменений
if git diff --quiet HEAD; then
    echo "✅ Нет локальных изменений"
else
    echo "⚠️  Есть незакоммиченные изменения"
    echo "   Хотите закоммитить? (y/n)"
    read -r COMMIT
    if [ "$COMMIT" = "y" ]; then
        echo "Введите сообщение коммита:"
        read -r COMMIT_MSG
        git add -A
        git commit -m "$COMMIT_MSG"
    fi
fi

# Пуш на GitHub
echo ""
echo "🚀 Выполняется git push -u origin main..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Пуш выполнен успешно!"
    echo ""
    echo "📱 URL репозитория:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "🌐 GitHub Pages (если включён):"
    echo "   https://${GITHUB_USERNAME}.github.io/${REPO_NAME}/"
    echo ""
else
    echo ""
    echo "❌ Ошибка при пуше"
    echo ""
    echo "Возможные причины:"
    echo "   1. Репозиторий не существует на GitHub"
    echo "   2. Неверные учётные данные"
    echo "   3. Проблемы с сетью"
    echo ""
    echo "Попробуйте создать репозиторий вручную:"
    echo "   https://github.com/new"
    exit 1
fi

echo "🎉 Готово!"
