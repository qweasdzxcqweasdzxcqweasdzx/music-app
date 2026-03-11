#!/usr/bin/env python3
"""
Скрипт для автоматического добавления цензурированных треков в базу данных

Использует логи стриминга для обнаружения треков, которые были:
- Заблюрены (beep вместо слов)
- Вырезаны (тишина)
- Удалены (ошибка воспроизведения)
- Clean/radio версии

Использование:
    python auto_add_censored_tracks.py
    
Или через API:
    POST /api/censored-tracks/auto-scan
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

# Добавляем backend в path
sys.path.insert(0, str(Path(__file__).parent))

from models.censored_tracks import CensoredTrackCreate, CensorshipType
from services.censored_tracks_service import censored_tracks_db


class CensoredTracksAutoScanner:
    """
    Автоматический сканер для обнаружения цензурированных треков
    
    Анализирует:
    1. Логи стриминга (ошибки воспроизведения)
    2. Логи Anti-Censorship системы
    3. JSON файлы с отчётами
    """
    
    def __init__(self, logs_dir: str = "/tmp/music-app"):
        self.logs_dir = Path(logs_dir)
        self.added_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def scan_streaming_logs(self) -> list:
        """
        Сканирование логов стриминга на предмет ошибок
        
        Ищет паттерны:
        - "error playing track"
        - "audio unavailable"
        - "track deleted"
        - "not available in your region"
        """
        censored_tracks = []
        log_files = [
            self.logs_dir / "streaming.log",
            self.logs_dir / "audio.log",
            self.logs_dir / "errors.log",
        ]
        
        # Паттерны для поиска
        error_patterns = [
            r'error.*playing.*track.*["\'](.+?)["\'].*by.*["\'](.+?)["\']',
            r'track.*["\'](.+?)["\'].*artist.*["\'](.+?)["\'].*unavailable',
            r'deleted.*track.*["\'](.+?)["\'].*["\'](.+?)["\']',
            r'not.*available.*["\'](.+?)["\'].*["\'](.+?)["\']',
        ]
        
        for log_file in log_files:
            if not log_file.exists():
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        for pattern in error_patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                title = match.group(1)
                                artist = match.group(2)
                                
                                censored_tracks.append({
                                    'title': title,
                                    'artist': artist,
                                    'platform_id': 'unknown',
                                    'platform': 'unknown',
                                    'censorship_type': CensorshipType.DELETED,
                                    'description': f'Ошибка воспроизведения: {line.strip()[:100]}',
                                    'source': 'log_file',
                                })
                                break
            except Exception as e:
                print(f"⚠️  Ошибка чтения {log_file}: {e}")
        
        return censored_tracks
    
    def scan_censorship_logs(self) -> list:
        """
        Сканирование логов Anti-Censorship системы
        
        Ищет треки, которые были определены как цензурированные
        """
        censored_tracks = []
        log_files = [
            self.logs_dir / "censorship.log",
            self.logs_dir / "blues_detection.log",
        ]
        
        # Паттерны для поиска
        patterns = [
            r'censored.*detected.*["\'](.+?)["\'].*["\'](.+?)["\'].*type[:\s]+(\w+)',
            r'clean.*version.*["\'](.+?)["\'].*["\'](.+?)["\']',
            r'radio.*edit.*["\'](.+?)["\'].*["\'](.+?)["\']',
        ]
        
        censorship_type_map = {
            'blurred': CensorshipType.BLURRED,
            'muted': CensorshipType.MUTED,
            'clean': CensorshipType.CLEAN_VERSION,
            'radio': CensorshipType.CLEAN_VERSION,
            'deleted': CensorshipType.DELETED,
            'replaced': CensorshipType.REPLACED,
        }
        
        for log_file in log_files:
            if not log_file.exists():
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        for pattern in patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                title = match.group(1)
                                artist = match.group(2)
                                ctype = match.group(3).lower() if match.lastindex >= 3 else 'clean'
                                
                                censored_type = censorship_type_map.get(
                                    ctype, 
                                    CensorshipType.CLEAN_VERSION
                                )
                                
                                censored_tracks.append({
                                    'title': title,
                                    'artist': artist,
                                    'platform_id': 'unknown',
                                    'platform': 'unknown',
                                    'censorship_type': censored_type,
                                    'description': f'Обнаружено в логе цензуры: {line.strip()[:100]}',
                                    'source': 'censorship_log',
                                })
                                break
            except Exception as e:
                print(f"⚠️  Ошибка чтения {log_file}: {e}")
        
        return censored_tracks
    
    def scan_json_reports(self) -> list:
        """
        Сканирование JSON файлов с отчётами о цензуре
        """
        censored_tracks = []
        report_files = [
            self.logs_dir / "censorship_reports.json",
            self.logs_dir / "blues_reports.json",
        ]
        
        for report_file in report_files:
            if not report_file.exists():
                continue
            
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Обработка разных форматов
                    if isinstance(data, list):
                        tracks = data
                    elif isinstance(data, dict) and 'tracks' in data:
                        tracks = data['tracks']
                    else:
                        tracks = []
                    
                    for track in tracks:
                        if isinstance(track, dict):
                            censored_tracks.append({
                                'title': track.get('title', 'Unknown'),
                                'artist': track.get('artist', 'Unknown'),
                                'platform_id': track.get('platform_id', 'unknown'),
                                'platform': track.get('platform', 'unknown'),
                                'censorship_type': CensorshipType(
                                    track.get('censorship_type', 'clean_version')
                                ),
                                'description': track.get('description'),
                                'timestamp_start': track.get('timestamp_start'),
                                'timestamp_end': track.get('timestamp_end'),
                                'censored_words': track.get('censored_words', []),
                                'source': 'json_report',
                            })
            except Exception as e:
                print(f"⚠️  Ошибка чтения {report_file}: {e}")
        
        return censored_tracks
    
    def add_to_database(self, tracks: list) -> tuple:
        """
        Добавление треков в базу данных
        
        Returns:
            (added_count, skipped_count, error_count)
        """
        added = 0
        skipped = 0
        errors = 0
        
        for track_data in tracks:
            try:
                track = CensoredTrackCreate(
                    title=track_data['title'],
                    artist=track_data['artist'],
                    original_title=track_data.get('original_title'),
                    platform_id=track_data.get('platform_id', 'unknown'),
                    platform=track_data.get('platform', 'unknown'),
                    censorship_type=track_data['censorship_type'],
                    description=track_data.get('description'),
                    timestamp_start=track_data.get('timestamp_start'),
                    timestamp_end=track_data.get('timestamp_end'),
                    censored_words=track_data.get('censored_words', []),
                    duration=track_data.get('duration'),
                    cover=track_data.get('cover'),
                    genres=track_data.get('genres', []),
                    notes=track_data.get('notes'),
                )
                
                result = censored_tracks_db.add_track(track)
                if result:
                    added += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                print(f"❌ Ошибка добавления трека: {e}")
                errors += 1
        
        return added, skipped, errors
    
    def run_full_scan(self) -> dict:
        """
        Запуск полного сканирования всех источников
        
        Returns:
            Статистика сканирования
        """
        print("🔍 Запуск сканирования источников...")
        
        all_tracks = []
        
        # Сканирование логов стриминга
        print("\n📁 Сканирование логов стриминга...")
        streaming_tracks = self.scan_streaming_logs()
        print(f"   Найдено: {len(streaming_tracks)} треков")
        all_tracks.extend(streaming_tracks)
        
        # Сканирование логов цензуры
        print("\n📁 Сканирование логов Anti-Censorship...")
        censorship_tracks = self.scan_censorship_logs()
        print(f"   Найдено: {len(censorship_tracks)} треков")
        all_tracks.extend(censorship_tracks)
        
        # Сканирование JSON отчётов
        print("\n📁 Сканирование JSON отчётов...")
        json_tracks = self.scan_json_reports()
        print(f"   Найдено: {len(json_tracks)} треков")
        all_tracks.extend(json_tracks)
        
        # Удаление дубликатов
        unique_tracks = []
        seen = set()
        for track in all_tracks:
            key = (track['title'].lower(), track['artist'].lower())
            if key not in seen:
                seen.add(key)
                unique_tracks.append(track)
        
        print(f"\n📊 Уникальных треков: {len(unique_tracks)}")
        
        # Добавление в базу
        print("\n💾 Добавление в базу данных...")
        added, skipped, errors = self.add_to_database(unique_tracks)
        
        return {
            'total_found': len(all_tracks),
            'unique': len(unique_tracks),
            'added': added,
            'skipped': skipped,
            'errors': errors,
        }


def main():
    parser = argparse.ArgumentParser(
        description='Автоматическое добавление цензурированных треков в базу'
    )
    parser.add_argument(
        '--logs-dir',
        default='/tmp/music-app',
        help='Директория с логами'
    )
    parser.add_argument(
        '--import-json',
        type=str,
        help='Импортировать из JSON файла'
    )
    parser.add_argument(
        '--export-json',
        type=str,
        help='Экспортировать в JSON файл'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Показать статистику базы'
    )
    
    args = parser.parse_args()
    
    scanner = CensoredTracksAutoScanner(logs_dir=args.logs_dir)
    
    if args.stats:
        stats = censored_tracks_db.get_statistics()
        print("\n📊 Статистика базы цензурированных треков:")
        print(f"   Всего: {stats.total_censored}")
        print(f"   По типам: {stats.by_type}")
        print(f"   По платформам: {stats.by_platform}")
        print(f"   По статусам: {stats.by_status}")
        print(f"   Найдено замен: {stats.replacements_found}")
        print(f"   Проверено: {stats.verified_count}")
        return
    
    if args.import_json:
        with open(args.import_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = censored_tracks_db.import_from_json(data)
        print(f"✅ Импортировано {count} треков из {args.import_json}")
        return
    
    if args.export_json:
        data = censored_tracks_db.export_to_json()
        with open(args.export_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Экспортировано {len(data)} треков в {args.export_json}")
        return
    
    # Запуск сканирования
    result = scanner.run_full_scan()
    
    print("\n" + "=" * 50)
    print("📊 Результаты сканирования:")
    print(f"   Всего найдено: {result['total_found']}")
    print(f"   Уникальных: {result['unique']}")
    print(f"   Добавлено: {result['added']}")
    print(f"   Пропущено (дубликаты): {result['skipped']}")
    print(f"   Ошибок: {result['errors']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
