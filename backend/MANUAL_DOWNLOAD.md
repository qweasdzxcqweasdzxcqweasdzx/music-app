# 📥 РУЧНОЕ СКАЧИВАНИЕ ТРЕКОВ (САМЫЙ НАДЁЖНЫЙ СПОСОБ)

## 🎯 Инструкция по шагам

### Шаг 1: Открой VK Music

```
https://vk.com/audios
```

### Шаг 2: Найди каждый трек из списка

**Приоритетные треки:**

```
1. OG Buda - ОПГ сити
2. OG Buda - Даёт 2
3. OG Buda - Групи
4. OG Buda - Выстрелы
5. OG Buda - Грусть
6. OG Buda - Добро Пожаловать
7. OG Buda - Грязный

8. Big Baby Tape - Bandana I
9. Big Baby Tape - KOOP
10. Big Baby Tape - So Icy Nihao

11. Pharaoh - Phuneral
12. Pharaoh - Правило

13. Агата Кристи - Опиум для никого
14. Агата Кристи - Декаданс
15. Агата Кристи - Ураган

16. Платина - Завидуют
17. Платина - Актриса

18. Soda Luv - Голодный пес
19. Soda Luv - G-SHOKK

20. Lil Krystalll - 2 бара
21. Lil Krystalll - Тик-так
```

### Шаг 3: Скачай через Telegram бота

**Боты для скачивания:**

1. **@vk_music_bot** — скачивание из VK
2. **@SaveMusicBot** — YouTube + VK
3. **@GoMusicBot** — VK Music

**Как использовать:**
1. Открой бота в Telegram
2. Отправь ссылку на трек из VK
3. Бот вернёт MP3 файл
4. Сохрани файл

### Шаг 4: Сохрани в папку

```
/home/c1ten12/music-app/backend/static/tracks/
```

**Структура:**
```
tracks/
├── OG_Buda/
│   ├── ОПГ_сити.mp3
│   ├── Даёт_2.mp3
│   └── ...
├── Big_Baby_Tape/
│   ├── Bandana_I.mp3
│   └── KOOP.mp3
└── ...
```

### Шаг 5: Обнови базу

После скачивания создай файл `update_local_tracks.py`:

```python
import json
import os

# Загрузка базы
with open('uncensored_pairs.json', 'r', encoding='utf-8') as f:
    pairs = json.load(f)

# Обновление путей
for hash_key, track in pairs.items():
    artist = track.get('artist', '')
    title = track.get('uncensored_title', '')
    
    # Поиск файла
    safe_name = f"{artist} - {title}".replace('/', '_')
    for root, dirs, files in os.walk('static/tracks'):
        for file in files:
            if safe_name[:20] in file and file.endswith('.mp3'):
                # Обновление пути
                local_path = f"/static/tracks/{file}"
                pairs[hash_key]['stream_url'] = local_path
                pairs[hash_key]['source'] = 'local'
                print(f"✅ Обновлено: {artist} - {title}")
                break

# Сохранение
with open('uncensored_pairs.json', 'w', encoding='utf-8') as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)
```

### Шаг 6: Перезапусти backend

```bash
pkill -f "uvicorn main_lite"
cd /home/c1ten12/music-app/backend
source venv/bin/activate
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
```

---

## ⚡ Быстрый старт

**Самый быстрый способ:**

1. Открой @vk_music_bot в Telegram
2. Скопируй названия треков выше
3. Найди каждый в VK → отправь боту
4. Сохрани MP3 файлы
5. Перемести в `backend/static/tracks/`

---

## 📁 Готовая структура

```bash
mkdir -p /home/c1ten12/music-app/backend/static/tracks
cd /home/c1ten12/music-app/backend/static/tracks

# После скачивания
mv ~/Downloads/*.mp3 ./
```

---

**🎯 ВАЖНО: СКАЧАТЬ ТРЕКИ НУЖНО СЕЙЧАС, ПОКА ОНИ ДОСТУПНЫ В VK!**
