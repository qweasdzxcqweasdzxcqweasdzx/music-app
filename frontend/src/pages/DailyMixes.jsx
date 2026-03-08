import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlayer } from '../contexts/PlayerContext';
import { musicAPI } from '../api/musicApi';
import PageTransition from '../components/PageTransition';
import AlbumCard from '../components/AlbumCard';
import { ClockIcon } from '../components/Icons';
import styles from './DailyMixes.module.css';

export default function DailyMixes() {
  const navigate = useNavigate();
  const { playTrack } = usePlayer();
  const [mixes, setMixes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expiresAt, setExpiresAt] = useState(null);

  useEffect(() => {
    loadMixes();
  }, []);

  const loadMixes = async () => {
    try {
      const data = await musicAPI.getDailyMixes();
      setMixes(data.mixes || []);
      setExpiresAt(data.expires_at);
    } catch (err) {
      console.error('Error loading daily mixes:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMixClick = (mix) => {
    // Переход на страницу плейлиста с треками микса
    navigate(`/playlist/${mix.id}`);
  };

  const handlePlayMix = (mix) => {
    // Воспроизведение первого трека микса
    if (mix.tracks && mix.tracks.length > 0) {
      playTrack(mix.tracks[0], mix.tracks);
    }
  };

  const formatExpires = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `Обновляется ${date.toLocaleDateString('ru-RU')}`;
  };

  if (isLoading) {
    return (
      <PageTransition>
        <div className={styles.dailyMixes}>
          <header className={styles.header}>
            <h1 className={styles.title}>Daily Mixes</h1>
          </header>
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>Генерация миксов...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className={styles.dailyMixes}>
        <header className={styles.header}>
          <h1 className={styles.title}>Daily Mixes</h1>
          {expiresAt && (
            <div className={styles.expires}>
              <ClockIcon size={16} />
              <span>{formatExpires(expiresAt)}</span>
            </div>
          )}
        </header>

        <div className={styles.description}>
          <p>6 персональных миксов, обновляемых каждый день</p>
          <p>Каждый микс основан на ваших любимых треках и артистах</p>
        </div>

        {mixes.length > 0 ? (
          <div className={styles.mixesGrid}>
            {mixes.map((mix, index) => (
              <div
                key={mix.id}
                className={styles.mixCard}
                onClick={() => handleMixClick(mix)}
              >
                <div className={styles.mixCoverWrapper}>
                  <img
                    src={mix.cover}
                    alt={mix.name}
                    className={styles.mixCover}
                    style={{ backgroundColor: mix.cover_color }}
                  />
                  <button
                    className={styles.playButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePlayMix(mix);
                    }}
                  >
                    ▶
                  </button>
                </div>
                <div className={styles.mixInfo}>
                  <h3 className={styles.mixName}>{mix.name}</h3>
                  <p className={styles.mixDescription}>{mix.description}</p>
                  <span className={styles.mixTracks}>
                    {mix.tracks_count} треков
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.empty}>
            <ClockIcon size={64} />
            <h2>Миксы генерируются</h2>
            <p>Начните слушать музыку чтобы получить персональные миксы</p>
          </div>
        )}

        <div className={styles.spacer} />
      </div>
    </PageTransition>
  );
}
