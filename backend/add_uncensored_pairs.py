#!/usr/bin/env python3
"""
Скрипт для массового добавления пар censored/uncensored в базу
"""

import json
import hashlib
import re
import os

# База известных пар censored/uncensored
pairs_to_add = [
    # Русские треки с пометками версий
    {
        "clean_title": "Опиум для никого (Radio Edit)",
        "uncensored_title": "Опиум для никого",
        "artist": "Агата Кристи",
        "stream_url": "https://youtube.com/watch?v=example1",
        "source": "youtube"
    },
    {
        "clean_title": "Убей мента (Clean)",
        "uncensored_title": "Убей мента",
        "artist": "Психея",
        "stream_url": "https://youtube.com/watch?v=example2",
        "source": "youtube"
    },
    # International examples
    {
        "clean_title": "Lose Yourself (Radio Edit)",
        "uncensored_title": "Lose Yourself",
        "artist": "Eminem",
        "stream_url": "https://youtube.com/watch?v=_Yhyp-_hX2s",
        "source": "youtube"
    },
    {
        "clean_title": "Bad Guy (Clean Version)",
        "uncensored_title": "Bad Guy",
        "artist": "Billie Eilish",
        "stream_url": "https://youtube.com/watch?v=DyDfgMOUjCI",
        "source": "youtube"
    },
    {
        "clean_title": "Godzilla (Clean)",
        "uncensored_title": "Godzilla (feat. Juice WRLD)",
        "artist": "Eminem",
        "stream_url": "https://youtube.com/watch?v=r_0JjY0e5jo",
        "source": "youtube"
    },
    # Russian rap examples
    {
        "clean_title": "ОПГ сити (Radio)",
        "uncensored_title": "ОПГ сити",
        "artist": "OG Buda",
        "stream_url": "https://vk.com/audio/og_buda_opg",
        "source": "vk"
    },
    {
        "clean_title": "Bandana (Clean)",
        "uncensored_title": "Bandana",
        "artist": "Big Baby Tape",
        "stream_url": "https://vk.com/audio/bbt_bandana",
        "source": "vk"
    },
    {
        "clean_title": "Завидуют (Radio Edit)",
        "uncensored_title": "Завидуют",
        "artist": "Платина",
        "stream_url": "https://vk.com/audio/platina_zaviduyut",
        "source": "vk"
    },
    {
        "clean_title": "2 бара (Clean)",
        "uncensored_title": "2 бара",
        "artist": "Lil Krystalll",
        "stream_url": "https://vk.com/audio/krystalll_2bara",
        "source": "vk"
    },
    {
        "clean_title": "Голодный пес (Radio)",
        "uncensored_title": "Голодный пес",
        "artist": "Soda Luv",
        "stream_url": "https://vk.com/audio/soda_golodny",
        "source": "vk"
    },
    # More examples
    {
        "clean_title": "Даёт 2 (Clean)",
        "uncensored_title": "Даёт 2",
        "artist": "OG Buda",
        "stream_url": "https://vk.com/audio/daet2",
        "source": "vk"
    },
    {
        "clean_title": "Групи (Radio)",
        "uncensored_title": "Групи",
        "artist": "OG Buda",
        "stream_url": "https://vk.com/audio/grupi",
        "source": "vk"
    },
    {
        "clean_title": "Выстрелы (Clean)",
        "uncensored_title": "Выстрелы",
        "artist": "OG Buda",
        "stream_url": "https://vk.com/audio/vystrely",
        "source": "vk"
    },
    {
        "clean_title": "Тик-так (Radio Edit)",
        "uncensored_title": "Тик-так",
        "artist": "Lil Krystalll",
        "stream_url": "https://vk.com/audio/tiktak",
        "source": "vk"
    },
    {
        "clean_title": "Актриса (Clean)",
        "uncensored_title": "Актриса",
        "artist": "Платина",
        "stream_url": "https://vk.com/audio/aktrisa",
        "source": "vk"
    },
    {
        "clean_title": "Братва на связи (Radio)",
        "uncensored_title": "Братва на связи",
        "artist": "Платина",
        "stream_url": "https://vk.com/audio/bratva",
        "source": "vk"
    },
    {
        "clean_title": "KOOP (Clean)",
        "uncensored_title": "KOOP",
        "artist": "Big Baby Tape",
        "stream_url": "https://vk.com/audio/koop",
        "source": "vk"
    },
    {
        "clean_title": "Даёт 2 (Clean)",
        "uncensored_title": "Даёт 2",
        "artist": "Scally Milano",
        "stream_url": "https://vk.com/audio/scally_daet2",
        "source": "vk"
    },
    {
        "clean_title": "Грусть (Radio)",
        "uncensored_title": "Грусть",
        "artist": "OG Buda",
        "stream_url": "https://vk.com/audio/grust",
        "source": "vk"
    },
    {
        "clean_title": "Добро Пожаловать (Clean)",
        "uncensored_title": "Добро Пожаловать",
        "artist": "OG Buda",
        "stream_url": "https://vk.com/audio/dobro",
        "source": "vk"
    },
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


def main():
    pairs_file = "uncensored_pairs.json"
    
    # Загрузка существующей базы
    if os.path.exists(pairs_file):
        with open(pairs_file, 'r', encoding='utf-8') as f:
            known_pairs = json.load(f)
        print(f"📦 Загружено существующих пар: {len(known_pairs)}")
    else:
        known_pairs = {}
        print("📝 Создаётся новая база")
    
    # Добавление новых пар
    added_count = 0
    skipped_count = 0
    
    for pair in pairs_to_add:
        clean = clean_title(pair["clean_title"])
        track_hash = hashlib.md5(clean.lower().encode('utf-8')).hexdigest()
        
        if track_hash not in known_pairs:
            known_pairs[track_hash] = {
                "clean_title": clean,
                "uncensored_title": pair["uncensored_title"],
                "artist": pair["artist"],
                "stream_url": pair["stream_url"],
                "source": pair["source"],
                "created_at": 0
            }
            added_count += 1
            print(f"✅ Добавлено: '{pair['clean_title']}' -> '{pair['uncensored_title']}'")
        else:
            skipped_count += 1
            print(f"⚠️  Уже есть: '{pair['clean_title']}'")
    
    # Сохранение
    with open(pairs_file, 'w', encoding='utf-8') as f:
        json.dump(known_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"📊 Итого в базе: {len(known_pairs)} пар")
    print(f"➕ Добавлено новых: {added_count}")
    print(f"⏭️  Пропущено: {skipped_count}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
