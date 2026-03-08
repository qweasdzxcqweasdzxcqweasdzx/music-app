import React, { useState, useContext, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { musicAPI } from '../api/musicApi';
import { PlayerContext } from '../contexts/PlayerContext';
import Skeleton from '../components/Skeleton';
import styles from './SmartMixer.module.css';

const MIX_MODES = [
  { id: 'smart', name: 'Умный микс', icon: '🧠', description: 'На основе ваших предпочтений' },
  { id: 'radio', name: 'Радио', icon: '📻', description: 'На основе трека' },
  { id: 'mood', name: 'Настроение', icon: '😊', description: 'По настроению' },
  { id: 'genre', name: 'Жанр', icon: '🎵', description: 'По жанру' },
];

const MOODS = [
  { id: 'happy', name: 'Счастливое', emoji: '😊', color: '#f1c40f' },
  { id: 'sad', name: 'Грустное', emoji: '😢', color: '#3498db' },
  { id: 'energetic', name: 'Энергичное', emoji: '⚡', color: '#e74c3c' },
  { id: 'chill', name: 'Спокойное', emoji: '😌', color: '#9b59b6' },
  { id: 'focus', name: 'Для работы', emoji: '🎯', color: '#1abc9c' },
];

const GENRES = [
  { id: 'pop', name: 'Pop' },
  { id: 'rock', name: 'Rock' },
  { id: 'electronic', name: 'Electronic' },
  { id: 'hip-hop', name: 'Hip-Hop' },
  { id: 'jazz', name: 'Jazz' },
  { id: 'classical', name: 'Classical' },
  { id: 'metal', name: 'Metal' },
  { id: 'indie', name: 'Indie' },
  { id: 'r&b', name: 'R&B' },
  { id: 'ambient', name: 'Ambient' },
];

const SOURCES = [
  { id: 'spotify', name: 'Spotify', color: '#1DB954' },
  { id: 'soundcloud', name: 'SoundCloud', color: '#ff5500' },
  { id: 'navidrome', name: 'Navidrome', color: '#3498db' },
];

export default function SmartMixer() {
  const { trackId } = useParams();
  const navigate = useNavigate();
  const { playTrack, playTracks } = useContext(PlayerContext);
  
  const [selectedMode, setSelectedMode] = useState('smart');
  const [selectedMood, setSelectedMood] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [selectedSources, setSelectedSources] = useState(['spotify', 'soundcloud', 'navidrome']);
  
  const [isLoading, setIsLoading] = useState(false);
  const [mixTracks, setMixTracks] = useState([]);
  const [mixName, setMixName] = useState('');
  const [error, setError] = useState(null);

  // Если передан trackId, включаем режим радио
  useEffect(() => {
    if (trackId) {
      setSelectedMode('radio');
      loadRadio(trackId);
    }
  }, [trackId]);

  // Загрузка радио
  const loadRadio = async (id) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await musicAPI.getInfiniteRadio(id, 50);
      setMixTracks(data.tracks || []);
      setMixName(`Радио: ${data.seed_track?.title || 'Трека'}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Загрузка микса
  const loadMix = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      let data;
      
      switch (selectedMode) {
        case 'smart':
          data = await musicAPI.getSmartMix(50, selectedSources.length ? selectedSources : null);
          setMixName('Умный микс');
          break;
        case 'mood':
          if (!selectedMood) {
            setError('Выберите настроение');
            setIsLoading(false);
            return;
          }
          data = await musicAPI.getMoodMix(selectedMood, 50);
          setMixName(`Настроение: ${MOODS.find(m => m.id === selectedMood)?.name}`);
          break;
        case 'genre':
          if (!selectedGenre) {
            setError('Выберите жанр');
            setIsLoading(false);
            return;
          }
          data = await musicAPI.getGenreMix(selectedGenre, 50, selectedSources.length ? selectedSources : null);
          setMixName(`Жанр: ${GENRES.find(g => g.id === selectedGenre)?.name}`);
          break;
        default:
          return;
      }
      
      setMixTracks(data.tracks || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Воспроизведение всего микса
  const playAll = () => {
    if (mixTracks.length) {
      playTrack(mixTracks[0], mixTracks);
    }
  };

  // Переключение источника
  const toggleSource = (sourceId) => {
    setSelectedSources(prev => 
      prev.includes(sourceId)
        ? prev.filter(s => s !== sourceId)
        : [...prev, sourceId]
    );
  };

  return (
    <div className={styles.smartMixer}>
      <header className={styles.header}>
        <h1>🎚️ Smart Mixer</h1>
        <p>Умное комбинирование музыки из разных источников</p>
      </header>

      {/* Выбор режима */}
      <div className={styles.modes}>
        {MIX_MODES.map(mode => (
          <div
            key={mode.id}
            className={`${styles.mode} ${selectedMode === mode.id ? styles.selected : ''}`}
            onClick={() => setSelectedMode(mode.id)}
          >
            <span className={styles.modeIcon}>{mode.icon}</span>
            <span className={styles.modeName}>{mode.name}</span>
            <span className={styles.modeDesc}>{mode.description}</span>
          </div>
        ))}
      </div>

      {/* Настройки режима */}
      {selectedMode === 'mood' && (
        <div className={styles.settings}>
          <h3>Выберите настроение</h3>
          <div className={styles.moods}>
            {MOODS.map(mood => (
              <button
                key={mood.id}
                className={`${styles.mood} ${selectedMood === mood.id ? styles.selected : ''}`}
                style={{ '--accent-color': mood.color }}
                onClick={() => setSelectedMood(mood.id)}
              >
                <span className={styles.moodEmoji}>{mood.emoji}</span>
                <span className={styles.moodName}>{mood.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {selectedMode === 'genre' && (
        <div className={styles.settings}>
          <h3>Выберите жанр</h3>
          <div className={styles.genres}>
            {GENRES.map(genre => (
              <button
                key={genre.id}
                className={`${styles.genre} ${selectedGenre === genre.id ? styles.selected : ''}`}
                onClick={() => setSelectedGenre(genre.id)}
              >
                {genre.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Выбор источников */}
      <div className={styles.settings}>
        <h3>Источники музыки</h3>
        <div className={styles.sources}>
          {SOURCES.map(source => (
            <label key={source.id} className={styles.source}>
              <input
                type="checkbox"
                checked={selectedSources.includes(source.id)}
                onChange={() => toggleSource(source.id)}
              />
              <span 
                className={styles.sourceIndicator}
                style={{ backgroundColor: source.color }}
              />
              <span className={styles.sourceName}>{source.name}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Кнопка генерации */}
      {selectedMode !== 'radio' && (
        <button 
          className={styles.generateButton}
          onClick={loadMix}
          disabled={isLoading}
        >
          {isLoading ? '⏳ Генерация...' : '🚀 Создать микс'}
        </button>
      )}

      {/* Ошибка */}
      {error && (
        <div className={styles.error}>
          ❌ {error}
        </div>
      )}

      {/* Результаты */}
      {(isLoading || mixTracks.length > 0) && (
        <div className={styles.results}>
          <div className={styles.resultsHeader}>
            <div>
              <h2>{mixName || 'Результаты'}</h2>
              <p>{mixTracks.length} треков</p>
            </div>
            {mixTracks.length > 0 && (
              <button className={styles.playAllButton} onClick={playAll}>
                ▶️ Воспроизвести всё
              </button>
            )}
          </div>

          {isLoading ? (
            <div className={styles.loading}>
              <Skeleton count={10} />
            </div>
          ) : (
            <div className={styles.tracks}>
              {mixTracks.map((track, index) => (
                <div
                  key={track.id || index}
                  className={styles.track}
                  onClick={() => playTrack(track, mixTracks, index)}
                >
                  <span className={styles.trackNumber}>{index + 1}</span>
                  <img 
                    src={track.cover || 'https://picsum.photos/seed/track/60/60'} 
                    alt={track.title}
                    className={styles.trackCover}
                  />
                  <div className={styles.trackInfo}>
                    <div className={styles.trackTitle}>{track.title}</div>
                    <div className={styles.trackArtist}>{track.artist}</div>
                  </div>
                  <span className={styles.trackSource} style={{ 
                    backgroundColor: SOURCES.find(s => s.id === track.source)?.color || '#666' 
                  }}>
                    {track.source}
                  </span>
                  <span className={styles.trackDuration}>
                    {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
