import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { musicAPI } from '../api/musicApi';
import './Search.module.css';
import styles from './GenreDetail.module.css';

const GenreDetail = () => {
  const { genreId } = useParams();
  const navigate = useNavigate();
  const [genreData, setGenreData] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const genreColors = {
    pop: '#1DB954',
    rock: '#E91429',
    hiphop: '#DC148C',
    electronic: '#0D73EC',
    indie: '#608108',
    metal: '#BC5900',
    jazz: '#477D95',
    classical: '#8C67AC',
    rnb: '#DC143C',
    country: '#5F4A3C',
    latin: '#E91E63',
    reggae: '#009688',
    blues: '#3F51B5',
    soul: '#9C27B0',
    funk: '#FF5722',
    ambient: '#00BCD4',
    house: '#FFC107',
    techno: '#607D8B',
    trance: '#9E9E9E',
    dubstep: '#795548',
    'drum-and-bass': '#3E2723',
    kpop: '#FF4081',
    jpop: '#E040FB',
    focus: '#536DFE',
  };

  const genreNames = {
    pop: 'Pop',
    rock: 'Rock',
    hiphop: 'Hip-Hop',
    electronic: 'Electronic',
    indie: 'Indie',
    metal: 'Metal',
    jazz: 'Jazz',
    classical: 'Classical',
    rnb: 'R&B',
    country: 'Country',
    latin: 'Latin',
    reggae: 'Reggae',
    blues: 'Blues',
    soul: 'Soul',
    funk: 'Funk',
    ambient: 'Ambient',
    house: 'House',
    techno: 'Techno',
    trance: 'Trance',
    dubstep: 'Dubstep',
    'drum-and-bass': 'Drum & Bass',
    kpop: 'K-Pop',
    jpop: 'J-Pop',
    focus: 'Focus',
  };

  useEffect(() => {
    const loadGenreTracks = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await musicAPI.getGenreTracks(genreId, 30);
        setTracks(data.tracks || []);
        setGenreData({
          id: genreId,
          name: genreNames[genreId] || genreId,
          color: genreColors[genreId] || '#1DB954',
          total: data.total || 0,
          source: data.source || 'mock',
        });
      } catch (err) {
        console.error('Error loading genre tracks:', err);
        setError('Не удалось загрузить треки. Попробуйте позже.');
        // Mock данные для демонстрации
        setGenreData({
          id: genreId,
          name: genreNames[genreId] || genreId,
          color: genreColors[genreId] || '#1DB954',
          total: 0,
          source: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    loadGenreTracks();
  }, [genreId]);

  const handlePlayTrack = (track) => {
    // Сохраняем в историю
    const history = JSON.parse(localStorage.getItem('listeningHistory') || '[]');
    history.push({ ...track, playedAt: new Date().toISOString() });
    localStorage.setItem('listeningHistory', history.slice(-100));

    // Отправляем событие плееру
    window.dispatchEvent(new CustomEvent('play-track', { detail: track }));
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Загрузка жанра...</p>
      </div>
    );
  }

  if (error && !genreData) {
    return (
      <div className={styles.error}>
        <p>{error}</p>
        <button onClick={() => navigate('/search')}>Вернуться к поиску</button>
      </div>
    );
  }

  return (
    <div className={styles.genreDetail}>
      {/* Header с градиентом */}
      <div 
        className={styles.header}
        style={{
          background: `linear-gradient(135deg, ${genreData.color}, #121212)`
        }}
      >
        <Link to="/search" className={styles.backLink}>
          <svg viewBox="0 0 16 16" width="24" height="24">
            <path fill="currentColor" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>
          </svg>
        </Link>
        <div className={styles.headerInfo}>
          <span className={styles.headerLabel}>Жанр</span>
          <h1 className={styles.headerTitle}>{genreData.name}</h1>
          <p className={styles.headerStats}>
            {tracks.length} треков
            {genreData.source === 'soundcloud' && ' • SoundCloud'}
            {genreData.source === 'mock' && ' • Демо режим'}
          </p>
        </div>
      </div>

      {/* Список треков */}
      <div className={styles.trackList}>
        {tracks.length === 0 ? (
          <div className={styles.empty}>
            <p>В этом жанре пока нет треков</p>
            <button onClick={() => navigate('/search')}>Найти музыку</button>
          </div>
        ) : (
          tracks.map((track, index) => (
            <div
              key={track.id || index}
              className={styles.trackRow}
              onClick={() => handlePlayTrack(track)}
            >
              <span className={styles.trackNumber}>{index + 1}</span>
              <img
                src={track.cover || track.artwork_url || 'https://via.placeholder.com/60'}
                alt={track.title}
                className={styles.trackImage}
                loading="lazy"
              />
              <div className={styles.trackInfo}>
                <span className={styles.trackTitle}>{track.title}</span>
                <span className={styles.trackArtist}>{track.artist || 'Неизвестный артист'}</span>
              </div>
              <span className={styles.trackDuration}>
                {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
              </span>
              <button className={styles.trackPlayBtn}>
                <svg viewBox="0 0 16 16" width="16" height="16">
                  <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default GenreDetail;
