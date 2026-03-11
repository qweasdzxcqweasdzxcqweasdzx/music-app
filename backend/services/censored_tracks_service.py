"""
Сервис для работы с локальной базой цензурированных треков

Использует SQLite для хранения данных.
Автоматически создаёт базу данных при первом запуске.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from models.censored_tracks import (
    CensoredTrack,
    CensoredTrackCreate,
    CensoredTrackUpdate,
    CensoredTrackSearch,
    CensorshipType,
    CensorshipSource,
    CensorshipStatistics,
)


class CensoredTracksDatabase:
    """
    Локальная база данных цензурированных треков
    
    Хранит информацию о треках, которые были:
    - Заблюрены (beep вместо слов)
    - Вырезаны (тишина вместо слов)
    - Заменены (другие слова)
    - Удалены из платформы
    - Clean/radio версии
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация базы данных
        
        Args:
            db_path: Путь к файлу базы данных.
                     По умолчанию: backend/censored_tracks.db
        """
        if db_path is None:
            # Путь по умолчанию
            base_dir = Path(__file__).parent
            db_path = base_dir / "censored_tracks.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Создание таблиц базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS censored_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    original_title TEXT,
                    censorship_type TEXT NOT NULL,
                    censorship_source TEXT NOT NULL DEFAULT 'auto_detect',
                    confidence REAL DEFAULT 1.0,
                    description TEXT,
                    timestamp_start INTEGER,
                    timestamp_end INTEGER,
                    censored_words TEXT DEFAULT '[]',
                    replacement_found INTEGER DEFAULT 0,
                    replacement_track_id TEXT,
                    replacement_url TEXT,
                    replacement_platform TEXT,
                    status TEXT DEFAULT 'pending',
                    verified_by TEXT,
                    verified_at TIMESTAMP,
                    duration INTEGER,
                    cover TEXT,
                    genres TEXT DEFAULT '[]',
                    notes TEXT,
                    report_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform_id, platform)
                )
            """)
            
            # Индексы для ускорения поиска
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_platform 
                ON censored_tracks(platform)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON censored_tracks(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_censorship_type 
                ON censored_tracks(censorship_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_artist 
                ON censored_tracks(artist)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_title 
                ON censored_tracks(title)
            """)
            
            conn.commit()
    
    def _dict_factory(self, cursor, row) -> Dict:
        """Конвертация строки результата в словарь"""
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}
    
    def add_track(self, track: CensoredTrackCreate) -> Optional[int]:
        """
        Добавление цензурированного трека в базу
        
        Args:
            track: Данные трека для добавления
            
        Returns:
            ID добавленного трека или None если уже существует
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                
                # Проверяем существование
                cursor.execute("""
                    SELECT id FROM censored_tracks 
                    WHERE platform_id = ? AND platform = ?
                """, (track.platform_id, track.platform))
                
                if cursor.fetchone():
                    print(f"⚠️  Трек {track.platform_id} уже существует в базе")
                    return None
                
                # Вставляем новый трек
                cursor.execute("""
                    INSERT INTO censored_tracks (
                        platform_id, platform, title, artist, original_title,
                        censorship_type, censorship_source, confidence,
                        description, timestamp_start, timestamp_end,
                        censored_words, duration, cover, genres, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track.platform_id,
                    track.platform,
                    track.title,
                    track.artist,
                    track.original_title,
                    track.censorship_type.value,
                    CensorshipSource.AUTO_DETECT.value,
                    1.0,
                    track.description,
                    track.timestamp_start,
                    track.timestamp_end,
                    json.dumps(track.censored_words or []),
                    track.duration,
                    track.cover,
                    json.dumps(track.genres or []),
                    track.notes,
                ))
                
                conn.commit()
                
                track_id = cursor.lastrowid
                print(f"✅ Добавлен цензурированный трек: {track.artist} - {track.title} (ID: {track_id})")
                return track_id
                
        except Exception as e:
            print(f"❌ Ошибка добавления трека: {e}")
            return None
    
    def get_track(self, track_id: int) -> Optional[Dict]:
        """Получение трека по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM censored_tracks WHERE id = ?
            """, (track_id,))
            
            row = cursor.fetchone()
            if row:
                # Парсим JSON поля
                row['censored_words'] = json.loads(row['censored_words'])
                row['genres'] = json.loads(row['genres'])
            return row
    
    def get_track_by_platform(self, platform_id: str, platform: str) -> Optional[Dict]:
        """Получение трека по ID платформы"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM censored_tracks 
                WHERE platform_id = ? AND platform = ?
            """, (platform_id, platform))
            
            row = cursor.fetchone()
            if row:
                row['censored_words'] = json.loads(row['censored_words'])
                row['genres'] = json.loads(row['genres'])
            return row
    
    def update_track(self, track_id: int, update: CensoredTrackUpdate) -> bool:
        """
        Обновление информации о треке
        
        Args:
            track_id: ID трека в базе
            update: Данные для обновления
            
        Returns:
            True если успешно
        """
        try:
            updates = []
            values = []
            
            if update.title is not None:
                updates.append("title = ?")
                values.append(update.title)
            if update.original_title is not None:
                updates.append("original_title = ?")
                values.append(update.original_title)
            if update.censorship_type is not None:
                updates.append("censorship_type = ?")
                values.append(update.censorship_type.value)
            if update.description is not None:
                updates.append("description = ?")
                values.append(update.description)
            if update.replacement_found is not None:
                updates.append("replacement_found = ?")
                values.append(1 if update.replacement_found else 0)
            if update.replacement_track_id is not None:
                updates.append("replacement_track_id = ?")
                values.append(update.replacement_track_id)
            if update.replacement_url is not None:
                updates.append("replacement_url = ?")
                values.append(update.replacement_url)
            if update.replacement_platform is not None:
                updates.append("replacement_platform = ?")
                values.append(update.replacement_platform)
            if update.status is not None:
                updates.append("status = ?")
                values.append(update.status)
            if update.verified_by is not None:
                updates.append("verified_by = ?")
                values.append(update.verified_by)
            if update.verified_at is not None:
                updates.append("verified_at = ?")
                values.append(update.verified_at.isoformat())
            if update.notes is not None:
                updates.append("notes = ?")
                values.append(update.notes)
            if update.report_count is not None:
                updates.append("report_count = ?")
                values.append(update.report_count)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(track_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE censored_tracks 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"❌ Ошибка обновления трека: {e}")
            return False
    
    def search(self, search: CensoredTrackSearch) -> List[Dict]:
        """
        Поиск треков в базе
        
        Args:
            search: Параметры поиска
            
        Returns:
            Список найденных треков
        """
        query_parts = []
        values = []
        
        if search.query:
            query_parts.append("(title LIKE ? OR artist LIKE ? OR original_title LIKE ?)")
            like_query = f"%{search.query}%"
            values.extend([like_query, like_query, like_query])
        
        if search.artist:
            query_parts.append("artist LIKE ?")
            values.append(f"%{search.artist}%")
        
        if search.platform:
            query_parts.append("platform = ?")
            values.append(search.platform)
        
        if search.censorship_type:
            query_parts.append("censorship_type = ?")
            values.append(search.censorship_type.value)
        
        if search.status:
            query_parts.append("status = ?")
            values.append(search.status)
        
        where_clause = ""
        if query_parts:
            where_clause = "WHERE " + " AND ".join(query_parts)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            
            sql = f"""
                SELECT * FROM censored_tracks 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            
            values.extend([search.limit, search.offset])
            cursor.execute(sql, values)
            
            rows = cursor.fetchall()
            
            # Парсим JSON поля
            for row in rows:
                row['censored_words'] = json.loads(row['censored_words'])
                row['genres'] = json.loads(row['genres'])
            
            return rows
    
    def get_statistics(self) -> CensorshipStatistics:
        """Получение статистики по базе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Общее количество
            cursor.execute("SELECT COUNT(*) FROM censored_tracks")
            total = cursor.fetchone()[0]
            
            # По типам цензуры
            cursor.execute("""
                SELECT censorship_type, COUNT(*) 
                FROM censored_tracks 
                GROUP BY censorship_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # По платформам
            cursor.execute("""
                SELECT platform, COUNT(*) 
                FROM censored_tracks 
                GROUP BY platform
            """)
            by_platform = {row[0]: row[1] for row in cursor.fetchall()}
            
            # По статусам
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM censored_tracks 
                GROUP BY status
            """)
            by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Найдены замены
            cursor.execute("SELECT COUNT(*) FROM censored_tracks WHERE replacement_found = 1")
            replacements = cursor.fetchone()[0]
            
            # Проверено
            cursor.execute("SELECT COUNT(*) FROM censored_tracks WHERE status = 'verified'")
            verified = cursor.fetchone()[0]
            
            return CensorshipStatistics(
                total_censored=total,
                by_type=by_type,
                by_platform=by_platform,
                by_status=by_status,
                replacements_found=replacements,
                verified_count=verified,
                last_updated=datetime.utcnow(),
            )
    
    def delete_track(self, track_id: int) -> bool:
        """Удаление трека из базы"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM censored_tracks WHERE id = ?
                """, (track_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка удаления трека: {e}")
            return False
    
    def get_all_pending(self) -> List[Dict]:
        """Получение всех непроверенных треков"""
        search = CensoredTrackSearch(status="pending", limit=1000)
        return self.search(search)
    
    def get_all_verified(self) -> List[Dict]:
        """Получение всех проверенных треков"""
        search = CensoredTrackSearch(status="verified", limit=1000)
        return self.search(search)
    
    def increment_report_count(self, track_id: int) -> bool:
        """Увеличение счётчика жалоб"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE censored_tracks 
                SET report_count = report_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (track_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def export_to_json(self) -> List[Dict]:
        """Экспорт всей базы в JSON формат"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM censored_tracks ORDER BY created_at DESC")
            
            rows = cursor.fetchall()
            
            # Парсим JSON поля
            for row in rows:
                row['censored_words'] = json.loads(row['censored_words'])
                row['genres'] = json.loads(row['genres'])
            
            return rows
    
    def import_from_json(self, data: List[Dict]) -> int:
        """
        Импорт треков из JSON
        
        Args:
            data: Список словарей с данными
            
        Returns:
            Количество импортированных треков
        """
        count = 0
        for item in data:
            try:
                track = CensoredTrackCreate(
                    title=item['title'],
                    artist=item['artist'],
                    original_title=item.get('original_title'),
                    platform_id=item['platform_id'],
                    platform=item['platform'],
                    censorship_type=CensorshipType(item['censorship_type']),
                    description=item.get('description'),
                    timestamp_start=item.get('timestamp_start'),
                    timestamp_end=item.get('timestamp_end'),
                    censored_words=item.get('censored_words', []),
                    duration=item.get('duration'),
                    cover=item.get('cover'),
                    genres=item.get('genres', []),
                    notes=item.get('notes'),
                )
                if self.add_track(track):
                    count += 1
            except Exception as e:
                print(f"⚠️  Ошибка импорта трека: {e}")
        
        return count


# Глобальный экземпляр
censored_tracks_db = CensoredTracksDatabase()
