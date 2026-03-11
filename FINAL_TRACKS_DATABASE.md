# 🎵 Итоговая база треков - Uncensored + Removed

## 📊 Статистика

| База | Записей | Описание |
|------|---------|----------|
| **uncensored_pairs.json** | 38 пар | Clean → Explicit версии |
| **removed_tracks_db.json** | 24 записи | Удалённые/скрытые альбомы и треки |

---

## 📁 Файлы

### Backend:
- `backend/uncensored_pairs.json` — база censored/uncensored пар
- `backend/removed_tracks_db.json` — база удалённых треков
- `backend/add_uncensored_pairs.py` — скрипт добавления uncensored пар
- `backend/add_russian_uncensored.py` — скрипт добавления русских треков
- `backend/create_removed_tracks_db.py` — скрипт создания базы removed
- `backend/search_and_add_uncensored.py` — автоматический поиск через YouTube

### API Endpoints:
- `GET /api/uncensored/check` — Проверка статуса цензуры
- `GET /api/uncensored/find` — Поиск uncensored версии
- `POST /api/uncensored/add-pair` — Добавление пары в базу
- `GET /api/removed/find` — Поиск удалённого трека
- `GET /api/removed/list` — Список удалённых треков

---

## 🎵 uncensored_pairs.json (38 пар)

### Русские артисты (26 пар):

| Артист | Треки |
|--------|-------|
| **OG Buda** | ОПГ сити, Даёт 2, Групи, Выстрелы, Грусть, Добро Пожаловать, Грязный |
| **Big Baby Tape** | Bandana, KOOP, Bandana I, Benzo Gang Money, So Icy Nihao |
| **Агата Кристи** | Опиум для никого, Декаданс, Ураган |
| **Платина** | Завидуют, Актриса, Братва на связи |
| **Soda Luv** | Голодный пес, G-SHOKK, КОТЬ! |
| **Lil Krystalll** | 2 бара, Тик-так |
| **Психея** | Убей мента, Всё идёт по плану |
| **Pharaoh** | Phuneral, Правило |
| **Friendly Thug 52 Ngg** | 52, Ngg |
| **Mayot & Seemee** | Scum Off The Pot |
| **Mayot** | FREERIO |
| **163onmyneck** | No Offence |
| **Коррозия Металла** | Бей чертей - спасай Россию |

### Международные артисты (12 пар):

| Артист | Треки |
|--------|-------|
| **Eminem** | Lose Yourself, Godzilla |
| **Billie Eilish** | Bad Guy |

---

## 📦 removed_tracks_db.json (24 записи)

### По типам:
- **album**: 12
- **track**: 10
- **catalog**: 2

### По артистам:

| Артист | Записей | Что удалено |
|--------|---------|-------------|
| **Pharaoh** | 4 | Pink Phloyd, Phuneral, Правило, Million Dollar Depression |
| **Агата Кристи** | 3 | Декаданс, Опиум, Ураган |
| **OG Buda** | 5 | ОПГ сити, Грязный, Выстрелы, Грусть, Добро Пожаловать |
| **Big Baby Tape** | 3 | ILOVEBENZO, KOOP, NOBODY |
| **Markscheider Kunst** | 2 | St. Petersburg — Kinshasa Transit, Utopia |
| **Слава КПСС** | 1 | 3 альбома (пропаганда) |
| **Scally Milano** | 1 | Ранний каталог |
| **Mayot & Seemee** | 1 | Scum Off The Pot |
| **163onmyneck** | 1 | No Offence |
| **Кино** | 1 | Классика с заглушками |
| **Bad Balance** | 1 | Город джунглей |
| **Guf / Centr** | 1 | Старые хиты 2000-х |

---

## 🔍 Как использовать

### 1. Проверка цензуры трека:
```bash
curl "http://localhost:8081/api/uncensored/check?track_id=1&title=Опиум+для+никого+(Radio+Edit)&artist=Агата+Кристи"
```

### 2. Поиск uncensored версии:
```bash
curl "http://localhost:8081/api/uncensored/find?track_id=1&title=Опиум+для+никого+(Radio+Edit)&artist=Агата+Кристи"
```

### 3. Поиск удалённого трека:
```bash
curl "http://localhost:8081/api/removed/find?artist=Pharaoh&title=Pink+Phloyd"
```

**Ответ:**
```json
{
  "status": "found",
  "item": {
    "type": "album",
    "artist": "Pharaoh",
    "title": "Pink Phloyd",
    "year": 2014,
    "reason": "Скрыт лейблом",
    "alt_sources": [
      "VK Music (зеркало)",
      "Telegram каналы",
      "Archive.org"
    ],
    "notes": "Культовый микстейп, доступен на неофициальных источниках"
  }
}
```

### 4. Список удалённых альбомов:
```bash
curl "http://localhost:8081/api/removed/list?type=album"
```

### 5. Добавление новой пары:
```bash
curl -X POST "http://localhost:8081/api/uncensored/add-pair" \
  -H "Content-Type: application/json" \
  -d '{
    "censored_title": "Название (Clean)",
    "uncensored_title": "Название (Explicit)",
    "artist": "Артист",
    "stream_url": "https://...",
    "source": "vk"
  }'
```

---

## 🎯 Источники для поиска

### Для uncensored версий:
1. **YouTube** — поиск с запросом `{artist} {track} explicit`
2. **SoundCloud** — часто есть оригиналы
3. **VK Music** — русские артисты
4. **Yandex Music** — альтернатива Spotify

### Для удалённых треков:
1. **VK Music** — зеркала и загрузки пользователей
2. **Telegram каналы** — утечки и редкие версии
3. **Archive.org** — архивные версии
4. **YouTube** — старые загрузки до удаления
5. **Vinyl rip** — для классики 80-90х

---

## ⚠️ Важные замечания

### Uncensored ≠ Removed

**Uncensored (Clean → Explicit):**
- Это те же треки, но в разных версиях
- Clean версия имеет маркеры: `(Clean)`, `(Radio Edit)`, `(Edited)`
- Explicit версия имеет маркеры: `(Explicit)`, `(Original)`, `(Uncut)`

**Removed (Удалённые):**
- Треки полностью недоступны на официальных платформах
- Причины: лицензия, политика, региональные ограничения
- Искать нужно на неофициальных источниках

---

## 📈 Планы развития

1. **Автоматический поиск** через YouTube API
2. **Интеграция с VK API** для поиска русских треков
3. **Crowdsourcing** — пользователи добавляют пары
4. **Audio fingerprinting** — точное matching по аудио
5. **Telegram бот** — уведомления о появлении треков

---

**🎉 ТЕПЕРЬ У ТЕБЯ ЕСТЬ ПОЛНАЯ БАЗА ДЛЯ ПОИСКА ОРИГИНАЛЬНЫХ ВЕРСИЙ!**
