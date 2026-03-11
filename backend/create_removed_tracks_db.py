#!/usr/bin/env python3
"""
База удалённых/скрытых треков и альбомов
Это не censored/explicit версии, а полностью удалённый контент
"""

import json
import os

# Удалённые/скрытые альбомы и треки
# Источники для поиска: VK, Telegram, Archive.org, зеркало
removed_content = [
    # ========== PHARAOH ==========
    {
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
    },
    {
        "type": "album",
        "artist": "Pharaoh",
        "title": "Phuneral",
        "year": 2017,
        "reason": "Скрыт лейблом",
        "alt_sources": ["VK Music", "Telegram"],
        "notes": "Доступен в VK"
    },
    {
        "type": "track",
        "artist": "Pharaoh",
        "title": "Правило",
        "year": 2017,
        "reason": "Скрыт лейблом",
        "alt_sources": ["Yandex Music", "VK Music"],
        "notes": "Доступен в Yandex Music"
    },
    {
        "type": "album",
        "artist": "Pharaoh",
        "title": "Million Dollar Depression",
        "year": 2016,
        "reason": "Скрыт лейблом",
        "alt_sources": ["VK Music", "Telegram"],
        "notes": "Доступен неофициально"
    },
    
    # ========== СЛАВА КПСС ==========
    {
        "type": "album",
        "artist": "Слава КПСС",
        "title": "Удалённые альбомы (3 шт)",
        "year": "2022-2024",
        "reason": "Подозрения в пропаганде веществ",
        "alt_sources": ["Telegram каналы", "Archive.org"],
        "notes": "Требуется поиск по названию альбома"
    },
    
    # ========== MARKSCHEIDER KUNST ==========
    {
        "type": "album",
        "artist": "Markscheider Kunst",
        "title": "St. Petersburg — Kinshasa Transit",
        "year": 2015,
        "reason": "Лицензионные ограничения",
        "alt_sources": ["VK Music", "Bandcamp"],
        "notes": "Доступен на Bandcamp группы"
    },
    {
        "type": "album",
        "artist": "Markscheider Kunst",
        "title": "Utopia",
        "year": 2018,
        "reason": "Лицензионные ограничения",
        "alt_sources": ["VK Music", "Bandcamp"],
        "notes": "Доступен на Bandcamp группы"
    },
    
    # ========== АГАТА КРИСТИ ==========
    {
        "type": "album",
        "artist": "Агата Кристи",
        "title": "Декаданс",
        "year": 1990,
        "reason": "Лицензионные ограничения",
        "alt_sources": ["VK Music", "Yandex Music", "YouTube"],
        "notes": "Доступен на Yandex Music"
    },
    {
        "type": "album",
        "artist": "Агата Кристи",
        "title": "Опиум",
        "year": 1995,
        "reason": "Лицензионные ограничения",
        "alt_sources": ["VK Music", "Yandex Music"],
        "notes": "Доступен на Yandex Music"
    },
    {
        "type": "album",
        "artist": "Агата Кристи",
        "title": "Ураган",
        "year": 1997,
        "reason": "Лицензионные ограничения",
        "alt_sources": ["VK Music", "Yandex Music"],
        "notes": "Доступен на Yandex Music"
    },
    
    # ========== OG BUDA ==========
    {
        "type": "track",
        "artist": "OG Buda",
        "title": "ОПГ сити",
        "year": 2019,
        "reason": "Региональные ограничения",
        "alt_sources": ["VK Music"],
        "notes": "Доступен в VK"
    },
    {
        "type": "track",
        "artist": "OG Buda",
        "title": "Грязный",
        "year": 2020,
        "reason": "Региональные ограничения",
        "alt_sources": ["VK Music"],
        "notes": "Доступен в VK"
    },
    {
        "type": "track",
        "artist": "OG Buda",
        "title": "Выстрелы",
        "year": 2020,
        "reason": "Региональные ограничения",
        "alt_sources": ["VK Music"],
        "notes": "Доступен в VK"
    },
    {
        "type": "track",
        "artist": "OG Buda",
        "title": "Грусть",
        "year": 2020,
        "reason": "Региональные ограничения",
        "alt_sources": ["VK Music"],
        "notes": "Доступен в VK"
    },
    {
        "type": "track",
        "artist": "OG Buda",
        "title": "Добро Пожаловать",
        "year": 2020,
        "reason": "Региональные ограничения",
        "alt_sources": ["VK Music"],
        "notes": "Доступен в VK"
    },
    
    # ========== BIG BABY TAPE ==========
    {
        "type": "album",
        "artist": "Big Baby Tape",
        "title": "ILOVEBENZO",
        "year": 2024,
        "reason": "Частично скрыт",
        "alt_sources": ["VK Music", "Telegram"],
        "notes": "Отдельные треки доступны"
    },
    {
        "type": "track",
        "artist": "Big Baby Tape",
        "title": "KOOP",
        "year": 2024,
        "reason": "Частично скрыт",
        "alt_sources": ["VK Music"],
        "notes": "Доступен в VK"
    },
    {
        "type": "track",
        "artist": "Big Baby Tape feat. Aarne & Toxi$",
        "title": "NOBODY",
        "year": 2024,
        "reason": "Скрыт лейблом",
        "alt_sources": ["VK Music", "Telegram"],
        "notes": "Требуется поиск"
    },
    
    # ========== SCALLY MILANO ==========
    {
        "type": "catalog",
        "artist": "Scally Milano",
        "title": "Ранний каталог",
        "year": "2019-2022",
        "reason": "Редактирован/скрыт для чистки текстов",
        "alt_sources": ["VK Music (старые версии)", "Archive.org"],
        "notes": "Оригинальные версии могут отличаться"
    },
    
    # ========== MAYOT & SEEMEE ==========
    {
        "type": "album",
        "artist": "Mayot & Seemee",
        "title": "Scum Off The Pot (серия)",
        "year": "2020-2022",
        "reason": "Часть треков заблюрена/скрыта",
        "alt_sources": ["VK Music", "Telegram"],
        "notes": "Отдельные треки в оригинале"
    },
    
    # ========== 163ONMYNECK ==========
    {
        "type": "album",
        "artist": "163onmyneck",
        "title": "No Offence",
        "year": 2022,
        "reason": "Глубокая модерация",
        "alt_sources": ["VK Music", "Yandex Music"],
        "notes": "Доступен с изменениями"
    },
    
    # ========== КИНО ==========
    {
        "type": "track",
        "artist": "Кино",
        "title": "Классические треки (заглушки)",
        "year": "1980-1990",
        "reason": "Звуковые заглушки в спорных местах",
        "alt_sources": ["Vinyl rip", "Archive.org", "YouTube (старые загрузки)"],
        "notes": "Оригинальные версии без заглушек редки"
    },
    
    # ========== BAD BALANCE ==========
    {
        "type": "track",
        "artist": "Bad Balance",
        "title": "Город джунглей",
        "year": 1990,
        "reason": "Периодически пропадает/возвращается",
        "alt_sources": ["VK Music", "YouTube", "Archive.org"],
        "notes": "Классика 90-х, доступна неофициально"
    },
    
    # ========== ГУФ / CENTR ==========
    {
        "type": "catalog",
        "artist": "Guf / Centr",
        "title": "Старые хиты (2000-е)",
        "year": "2000-2010",
        "reason": "Ручная проверка лейблами",
        "alt_sources": ["VK Music", "Telegram каналы"],
        "notes": "Доступны с задержкой"
    },
]


def main():
    output_file = "removed_tracks_db.json"
    
    # Сохранение базы
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(removed_content, f, ensure_ascii=False, indent=2)
    
    print("="*70)
    print("📦 БАЗА УДАЛЁННЫХ/СКРЫТЫХ ТРЕКОВ СОЗДАНА")
    print("="*70)
    print(f"\n💾 Файл: {output_file}")
    print(f"📊 Всего записей: {len(removed_content)}")
    
    # Группировка по типам
    by_type = {}
    for item in removed_content:
        t = item["type"]
        if t not in by_type:
            by_type[t] = 0
        by_type[t] += 1
    
    print("\n📋 По типам:")
    for t, count in sorted(by_type.items()):
        print(f"   • {t}: {count}")
    
    # Группировка по артистам
    by_artist = {}
    for item in removed_content:
        artist = item["artist"]
        if artist not in by_artist:
            by_artist[artist] = 0
        by_artist[artist] += 1
    
    print("\n🎤 По артистам:")
    for artist, count in sorted(by_artist.items(), key=lambda x: -x[1]):
        print(f"   • {artist}: {count}")
    
    print("\n" + "="*70)
    print("✅ Для интеграции с API создай endpoint /api/removed/find")
    print("="*70)


if __name__ == "__main__":
    main()
