import { useState, useEffect } from 'react';
import { usePlayer } from '../contexts/PlayerContext';
import { BackIcon, HeartIcon, ShuffleIcon, RepeatIcon, QueueIcon, DownloadIcon, MoreIcon, VolumeIcon, LyricsIcon } from '../components/Icons';
import { useNavigate } from 'react-router-dom';
import { musicAPI } from '../api/musicApi';
import styles from './FullPlayer.module.css';

export default function FullPlayer() {
  const navigate = useNavigate();
  const {
    currentTrack,
    isPlaying,
    isLoading,
    error,
    togglePlay,
    playNext,
    playPrevious,
    progress,
    duration,
    isLiked,
    toggleLike,
    isShuffle,
    toggleShuffle,
    repeatMode,
    toggleRepeat,
    volume,
    setVolume
  } = usePlayer();

  const [showVolume, setShowVolume] = useState(false);
  const [showLyrics, setShowLyrics] = useState(false);
  const [lyrics, setLyrics] = useState(null);
  const [lyricsLoading, setLyricsLoading] = useState(false);

  // Загрузка текста песни
  useEffect(() => {
    if (showLyrics && currentTrack && !lyrics) {
      loadLyrics();
    }
  }, [showLyrics, currentTrack]);

  const loadLyrics = async () => {
    if (!currentTrack) return;
    
    setLyricsLoading(true);
    try {
      const data = await musicAPI.getLyrics(
        currentTrack.id || currentTrack.title,
        currentTrack.title,
        currentTrack.artist
      );
      setLyrics(data);
    } catch (err) {
      console.error('Error loading lyrics:', err);
    } finally {
      setLyricsLoading(false);
    }
  };

  if (!currentTrack) return null;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = x / rect.width;
    const newProgress = percent * duration;
    // Здесь должен быть вызов seek из контекста
    console.log('Seek to:', newProgress);
  };

  return (
    <div className={styles.fullPlayer}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate(-1)}>
          <BackIcon size={24} />
        </button>
        <span className={styles.headerTitle}>Сейчас играет</span>
        <button className={styles.moreBtn}>
          <MoreIcon size={24} />
        </button>
      </div>

      {error && (
        <div className={styles.errorMessage}>
          <span>{error}</span>
          <button onClick={togglePlay}>Повторить</button>
        </div>
      )}

      <div className={styles.content}>
        <div className={styles.coverWrapper}>
          <img
            src={currentTrack.cover || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23282828" width="100" height="100"/></svg>'}
            alt={currentTrack.title}
            className={`${styles.cover} ${isLoading ? styles.loading : ''}`}
          />
          {isLoading && (
            <div className={styles.coverLoadingOverlay}>
              <div className={styles.spinner} />
            </div>
          )}
        </div>

        <div className={styles.trackInfo}>
          <div className={styles.trackName}>{currentTrack.title}</div>
          <div className={styles.trackArtist}>{currentTrack.artist}</div>
        </div>

        <div className={styles.progressSection}>
          <div 
            className={styles.progressBar}
            onClick={handleSeek}
          >
            <div 
              className={styles.progress}
              style={{ width: `${(progress / duration) * 100}%` }}
            />
          </div>
          <div className={styles.time}>
            <span>{formatTime(progress)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className={styles.controls}>
          <button 
            className={`${styles.controlBtn} ${isShuffle ? styles.active : ''}`}
            onClick={toggleShuffle}
          >
            <ShuffleIcon size={20} />
          </button>
          
          <button className={styles.controlBtn} onClick={playPrevious}>
            <BackIcon size={28} />
          </button>
          
          <button className={styles.playBtn} onClick={togglePlay}>
            {isPlaying ? (
              <svg width={32} height={32} viewBox="0 0 24 24" fill="#121212">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
            ) : (
              <svg width={32} height={32} viewBox="0 0 24 24" fill="#121212">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>
          
          <button className={styles.controlBtn} onClick={playNext}>
            <svg width={28} height={28} viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 6v12l8.5-6L8 18V6zm9 0h2v12h-2V6z" />
            </svg>
          </button>
          
          <button 
            className={`${styles.controlBtn} ${repeatMode !== 'off' ? styles.active : ''}`}
            onClick={toggleRepeat}
          >
            <RepeatIcon size={20} mode={repeatMode} />
          </button>
        </div>

        <div className={styles.bottomControls}>
          <button
            className={`${styles.iconBtn} ${isLiked ? styles.liked : ''}`}
            onClick={toggleLike}
          >
            <HeartIcon size={24} filled={isLiked} />
          </button>

          <button className={styles.iconBtn} onClick={() => navigate('/queue')}>
            <QueueIcon size={24} />
          </button>

          <button 
            className={styles.iconBtn}
            onClick={() => setShowLyrics(true)}
          >
            <LyricsIcon size={24} />
          </button>

          <div className={styles.volumeWrapper}>
            <button
              className={styles.iconBtn}
              onMouseEnter={() => setShowVolume(true)}
              onMouseLeave={() => setShowVolume(false)}
            >
              <VolumeIcon size={24} />
            </button>
            {showVolume && (
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={volume}
                onChange={(e) => setVolume(parseFloat(e.target.value))}
                className={styles.volumeSlider}
              />
            )}
          </div>

          <button className={styles.iconBtn}>
            <DownloadIcon size={24} />
          </button>
        </div>
      </div>

      {/* Модальное окно с текстом песни */}
      {showLyrics && (
        <div className={styles.lyricsModal} onClick={() => setShowLyrics(false)}>
          <div className={styles.lyricsContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.lyricsHeader}>
              <h2>Текст песни</h2>
              <button onClick={() => setShowLyrics(false)}>✕</button>
            </div>
            
            <div className={styles.lyricsBody}>
              {lyricsLoading ? (
                <div className={styles.lyricsLoading}>
                  <div className={styles.spinner}></div>
                  <p>Загрузка текста...</p>
                </div>
              ) : lyrics && lyrics.lyrics ? (
                <div className={styles.lyricsText}>
                  <h3>{lyrics.title || currentTrack.title}</h3>
                  <p className={styles.lyricsArtist}>{lyrics.artist || currentTrack.artist}</p>
                  <pre>{lyrics.lyrics}</pre>
                  {lyrics.url && (
                    <a 
                      href={lyrics.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles.lyricsSource}
                    >
                      Источник: {lyrics.provider || 'Genius'}
                    </a>
                  )}
                </div>
              ) : (
                <div className={styles.lyricsNotAvailable}>
                  <LyricsIcon size={48} />
                  <p>Текст недоступен</p>
                  <span>Для этой песни нет текста</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className={styles.nextUp}>
        <div className={styles.nextUpTitle}>Далее:</div>
        <div className={styles.nextUpTrack}>Следующий трек</div>
      </div>
    </div>
  );
}
