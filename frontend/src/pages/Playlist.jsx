import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import PageTransition from '../components/PageTransition';
import { usePlayer } from '../contexts/PlayerContext';
import { PlayIcon, PauseIcon, BackIcon, MoreIcon, HeartIcon, DownloadIcon } from '../components/Icons';
import TrackCard from '../components/TrackCard';
import styles from './Playlist.module.css';

// Моковые данные для плейлистов
const mockPlaylists = {
  'favorites': {
    id: 'favorites',
    name: 'Любимое',
    description: 'Ваши любимые треки',
    cover: 'https://picsum.photos/seed/favorites/300/300',
    isPublic: false,
    owner: 'Вы',
    tracks: [
      { id: 1, title: 'Bohemian Rhapsody', artist: 'Queen', cover: 'https://picsum.photos/seed/queen/300/300', duration: 354 },
      { id: 2, title: 'Hotel California', artist: 'Eagles', cover: 'https://picsum.photos/seed/eagles/300/300', duration: 391 },
      { id: 3, title: 'Stairway to Heaven', artist: 'Led Zeppelin', cover: 'https://picsum.photos/seed/ledzep/300/300', duration: 482 },
      { id: 4, title: 'Imagine', artist: 'John Lennon', cover: 'https://picsum.photos/seed/lennon/300/300', duration: 183 },
      { id: 5, title: 'Smells Like Teen Spirit', artist: 'Nirvana', cover: 'https://picsum.photos/seed/nirvana/300/300', duration: 301 },
    ]
  },
  'workout': {
    id: 'workout',
    name: 'Для тренировок',
    description: 'Энергичная музыка для спорта',
    cover: 'https://picsum.photos/seed/workout/300/300',
    isPublic: true,
    owner: 'Вы',
    tracks: [
      { id: 6, title: 'Blinding Lights', artist: 'The Weeknd', cover: 'https://picsum.photos/seed/weeknd/300/300', duration: 200 },
      { id: 7, title: 'Uptown Funk', artist: 'Bruno Mars', cover: 'https://picsum.photos/seed/brunomars/300/300', duration: 269 },
      { id: 8, title: 'Bad Guy', artist: 'Billie Eilish', cover: 'https://picsum.photos/seed/billie/300/300', duration: 194 },
    ]
  },
  'car': {
    id: 'car',
    name: 'В машину',
    description: 'Для долгих поездок',
    cover: 'https://picsum.photos/seed/car/300/300',
    isPublic: true,
    owner: 'Вы',
    tracks: [
      { id: 9, title: 'Shape of You', artist: 'Ed Sheeran', cover: 'https://picsum.photos/seed/edsheeran/300/300', duration: 233 },
      { id: 10, title: 'Someone Like You', artist: 'Adele', cover: 'https://picsum.photos/seed/adele/300/300', duration: 285 },
      { id: 11, title: 'Rolling in the Deep', artist: 'Adele', cover: 'https://picsum.photos/seed/adele2/300/300', duration: 228 },
      { id: 12, title: 'Midnight City', artist: 'M83', cover: 'https://picsum.photos/seed/m83/300/300', duration: 243 },
    ]
  },
  'default': {
    id: 'default',
    name: 'Новый плейлист',
    description: 'Описание плейлиста',
    cover: 'https://picsum.photos/seed/playlist/300/300',
    isPublic: false,
    owner: 'Вы',
    tracks: []
  }
};

export default function Playlist() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { playTrack, currentTrack, isPlaying } = usePlayer();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({ name: '', description: '' });
  const [showMenu, setShowMenu] = useState(false);

  const playlist = mockPlaylists[id] || mockPlaylists['default'];
  const isPlayingPlaylist = currentTrack && playlist.tracks.some(t => t.id === currentTrack.id);

  const handlePlay = () => {
    if (playlist.tracks.length > 0) {
      playTrack(playlist.tracks[0], playlist.tracks);
    }
  };

  const handleEdit = () => {
    setEditData({ name: playlist.name, description: playlist.description });
    setIsEditing(true);
  };

  const handleSave = () => {
    // Здесь будет логика сохранения на бэкенде
    setIsEditing(false);
  };

  const handleDeleteTrack = (trackId) => {
    // Здесь будет логика удаления трека
    console.log('Delete track:', trackId);
  };

  const totalDuration = playlist.tracks.reduce((acc, track) => acc + track.duration, 0);
  const hours = Math.floor(totalDuration / 3600);
  const minutes = Math.floor((totalDuration % 3600) / 60);
  const durationText = hours > 0 
    ? `${hours} ч ${minutes} мин` 
    : `${minutes} мин`;

  if (isEditing) {
    return (
      <div className={styles.editMode}>
        <div className={styles.editHeader}>
          <button className={styles.backBtn} onClick={() => setIsEditing(false)}>
            <BackIcon size={24} />
          </button>
          <h1 className={styles.editTitle}>Редактировать</h1>
          <button className={styles.saveBtn} onClick={handleSave}>
            Сохранить
          </button>
        </div>

        <div className={styles.editForm}>
          <div className={styles.coverEdit}>
            <img src={playlist.cover} alt={playlist.name} className={styles.coverEditImg} />
            <button className={styles.changeCoverBtn}>Изменить</button>
          </div>

          <input
            type="text"
            className={styles.nameInput}
            value={editData.name}
            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            placeholder="Название плейлиста"
          />

          <textarea
            className={styles.descInput}
            value={editData.description}
            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            placeholder="Описание (необязательно)"
            rows={3}
          />

          <label className={styles.publicToggle}>
            <input type="checkbox" defaultChecked={playlist.isPublic} />
            <span>Публичный плейлист</span>
          </label>
        </div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className={styles.playlist}>
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <button className={styles.backBtn} onClick={() => navigate(-1)}>
              <BackIcon size={24} />
            </button>

          <div className={styles.topRow}>
            <img 
              src={playlist.cover} 
              alt={playlist.name}
              className={styles.cover}
            />

            <div className={styles.info}>
              <span className={styles.type}>Плейлист</span>
              <h1 className={styles.name}>{playlist.name}</h1>
              <p className={styles.description}>{playlist.description}</p>
              <div className={styles.meta}>
                <span className={styles.owner}>{playlist.owner}</span>
                <span className={styles.separator}>•</span>
                <span className={styles.count}>{playlist.tracks.length} треков</span>
                <span className={styles.separator}>•</span>
                <span className={styles.duration}>{durationText}</span>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.actions}>
          <button 
            className={styles.playBtn}
            onClick={handlePlay}
            disabled={playlist.tracks.length === 0}
          >
            {isPlayingPlaylist && isPlaying ? (
              <PauseIcon size={28} fill="#121212" />
            ) : (
              <PlayIcon size={28} fill="#121212" />
            )}
          </button>
          <button className={styles.iconBtn}>
            <HeartIcon size={28} />
          </button>
          <button className={styles.iconBtn}>
            <DownloadIcon size={28} />
          </button>
          <button className={styles.iconBtn} onClick={() => setShowMenu(!showMenu)}>
            <MoreIcon size={24} />
          </button>
        </div>

        {showMenu && (
          <div className={styles.menu}>
            <button className={styles.menuItem} onClick={handleEdit}>
              Редактировать плейлист
            </button>
            <button className={styles.menuItem}>
              Добавить треки
            </button>
            <button className={styles.menuItem}>
              Поделиться
            </button>
            <button className={styles.menuItemDanger}>
              Удалить плейлист
            </button>
          </div>
        )}
      </div>

      <div className={styles.tracksHeader}>
        <span className={styles.trackNumber}>#</span>
        <span className={styles.trackTitle}>Название</span>
        <span className={styles.trackDuration}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" />
          </svg>
        </span>
      </div>

      <div className={styles.trackList}>
        {playlist.tracks.length > 0 ? (
          playlist.tracks.map((track, index) => (
            <div key={track.id} className={styles.trackRow}>
              <span className={styles.trackNumber}>{index + 1}</span>
              <div className={styles.trackCardWrapper}>
                <TrackCard track={track} queue={playlist.tracks} />
              </div>
              <button 
                className={styles.deleteBtn}
                onClick={() => handleDeleteTrack(track.id)}
              >
                ✕
              </button>
            </div>
          ))
        ) : (
          <div className={styles.empty}>
            <p>В этом плейлисте пока нет треков</p>
            <button className={styles.addBtn}>Добавить треки</button>
          </div>
        )}
      </div>

      <div className={styles.spacer} />
      </div>
    </PageTransition>
  );
}
