#!/usr/bin/env python3
"""
Автоматический поиск и добавление uncensored версий треков в базу
Использует YouTube Data API или поиск через yt-dlp
"""

import json
import hashlib
import re
import os
import sys

# Пытаемся импортировать yt_dlp
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    print("⚠️  yt-dlp не установлен. Установите: pip install yt-dlp")

# Список треков для поиска
tracks_to_find = [
    # Агата Кристи
    {"artist": "Агата Кристи", "clean": "Опиум для никого", "query": "Агата Кристи Опиум для никого оригинал"},
    {"artist": "Агата Кристи", "clean": "Декаданс", "query": "Агата Кристи Декаданс оригинал"},
    {"artist": "Агата Кристи", "clean": "Ураган", "query": "Агата Кристи Ураган оригинал"},
    
    # Pharaoh
    {"artist": "Pharaoh", "clean": "Pink Phloyd", "query": "Pharaoh Pink Phloyd album"},
    {"artist": "Pharaoh", "clean": "Phuneral", "query": "Pharaoh Phuneral album"},
    {"artist": "Pharaoh", "clean": "Правило", "query": "Pharaoh Правило трек"},
    
    # OG Buda
    {"artist": "OG Buda", "clean": "ОПГ сити", "query": "OG Buda ОПГ сити оригинал"},
    {"artist": "OG Buda", "clean": "Даёт 2", "query": "OG Buda Даёт 2 оригинал"},
    {"artist": "OG Buda", "clean": "Групи", "query": "OG Buda Групи оригинал"},
    {"artist": "OG Buda", "clean": "Выстрелы", "query": "OG Buda Выстрелы оригинал"},
    {"artist": "OG Buda", "clean": "Грусть", "query": "OG Buda Грусть оригинал"},
    {"artist": "OG Buda", "clean": "Добро Пожаловать", "query": "OG Buda Добро Пожаловать оригинал"},
    
    # Big Baby Tape
    {"artist": "Big Baby Tape", "clean": "Bandana", "query": "Big Baby Tape Bandana album 2018"},
    {"artist": "Big Baby Tape", "clean": "KOOP", "query": "Big Baby Tape KOOP трек"},
    {"artist": "Big Baby Tape", "clean": "Benzo Gang Money", "query": "Big Baby Tape Benzo Gang Money"},
    
    # Платина
    {"artist": "Платина", "clean": "Завидуют", "query": "Платина Завидуют оригинал"},
    {"artist": "Платина", "clean": "Актриса", "query": "Платина Актриса оригинал"},
    {"artist": "Платина", "clean": "Братва на связи", "query": "Платина Братва на связи"},
    
    # Scally Milano
    {"artist": "Scally Milano", "clean": "Даёт 2", "query": "Scally Milano Даёт 2 оригинал"},
    
    # Lil Krystalll
    {"artist": "Lil Krystalll", "clean": "2 бара", "query": "Lil Krystalll 2 бара оригинал"},
    {"artist": "Lil Krystalll", "clean": "Тик-так", "query": "Lil Krystalll Тик-так оригинал"},
    
    # Soda Luv
    {"artist": "Soda Luv", "clean": "Голодный пес", "query": "Soda Luv Голодный пес оригинал"},
    {"artist": "Soda Luv", "clean": "G-SHOKK", "query": "Soda Luv G-SHOKK"},
    
    # Психея
    {"artist": "Психея", "clean": "Убей мента", "query": "Психея Убей мента оригинал"},
    
    # Коррозия Металла
    {"artist": "Коррозия Металла", "clean": "Бей чертей", "query": "Коррозия Металла Бей чертей спасай Россию"},
    
    # Тимур Муцураев (пример)
    {"artist": "Тимур Муцураев", "clean": "Чеченская республика", "query": "Тимур Муцураев песни чеченский язык"},
]


def clean_title(title):
    """Очистка названия от маркеров цензуры"""
    patterns = [
        r'\s*\([^)]*(clean|radio|edit|censored)[^)]*\)',
        r'\s*\[[^\]]*(clean|radio|edit|censored)[^\]]*\]',
        r'\s*-\s*(Clean Version|Radio Edit|Edited)',
    ]
    result = title
    for pattern in patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    return result.strip()


def title_hash(title):
    """Создание хэша названия"""
    cleaned = clean_title(title)
    return hashlib.md5(cleaned.lower().encode('utf-8')).hexdigest()


def search_youtube(query, limit=5):
    """Поиск на YouTube через yt-dlp"""
    if not YTDLP_AVAILABLE:
        return []
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{limit}:{query}"
            results = ydl.extract_info(search_query, download=False)
            
            tracks = []
            for entry in results.get('entries', []):
                if entry and entry.get('_type') == 'video':
                    tracks.append({
                        'title': entry.get('title', ''),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                        'duration': entry.get('duration', 0),
                        'thumbnail': entry.get('thumbnail', '')
                    })
            return tracks
    except Exception as e:
        print(f"  ❌ Ошибка поиска YouTube: {e}")
        return []


def find_best_match(results, expected_artist):
    """Выбор лучшего результата из поиска"""
    if not results:
        return None
    
    # Первый результат обычно наиболее релевантный
    return results[0]


def add_to_database(clean_title, uncensored_title, artist, stream_url, source="youtube"):
    """Добавление пары в базу"""
    pairs_file = "uncensored_pairs.json"
    
    # Загрузка существующей базы
    if os.path.exists(pairs_file):
        with open(pairs_file, 'r', encoding='utf-8') as f:
            known_pairs = json.load(f)
    else:
        known_pairs = {}
    
    # Добавление новой пары
    track_hash = title_hash(clean_title)
    
    if track_hash not in known_pairs:
        known_pairs[track_hash] = {
            "clean_title": clean_title,
            "uncensored_title": uncensored_title,
            "artist": artist,
            "stream_url": stream_url,
            "source": source,
            "created_at": 0
        }
        
        # Сохранение
        with open(pairs_file, 'w', encoding='utf-8') as f:
            json.dump(known_pairs, f, ensure_ascii=False, indent=2)
        
        return True
    return False


def main():
    print("=" * 60)
    print("🔍 АВТОМАТИЧЕСКИЙ ПОИСК UNCENSORED ВЕРСИЙ")
    print("=" * 60)
    
    if not YTDLP_AVAILABLE:
        print("\n⚠️  yt-dlp не установлен!")
        print("   Установите командой: pip install yt-dlp")
        print("\nИли добавьте треки вручную через add_uncensored_pairs.py")
        return
    
    found_count = 0
    not_found_count = 0
    
    for i, track in enumerate(tracks_to_find, 1):
        print(f"\n[{i}/{len(tracks_to_find)}] {track['artist']} - {track['clean']}")
        
        # Поиск на YouTube
        print(f"  🔍 Поиск: {track['query']}")
        results = search_youtube(track['query'], limit=3)
        
        if results:
            best = find_best_match(results, track['artist'])
            if best:
                print(f"  ✅ Найдено: {best['title'][:60]}")
                
                # Добавление в базу
                added = add_to_database(
                    clean_title=track['clean'],
                    uncensored_title=best['title'],
                    artist=track['artist'],
                    stream_url=best['url'],
                    source="youtube"
                )
                
                if added:
                    print(f"  💾 Добавлено в базу")
                    found_count += 1
                else:
                    print(f"  ⚠️  Уже есть в базе")
            else:
                print(f"  ❌ Не найдено")
                not_found_count += 1
        else:
            print(f"  ❌ Нет результатов")
            not_found_count += 1
        
        # Небольшая задержка между запросами
        import time
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Найдено и добавлено: {found_count}")
    print(f"  ❌ Не найдено: {not_found_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
