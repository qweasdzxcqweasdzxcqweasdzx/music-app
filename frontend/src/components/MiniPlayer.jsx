import { useNavigate } from 'react-router-dom';
import { usePlayer } from '../contexts/PlayerContext';
import { PlayIcon, PauseIcon, NextIcon, PrevIcon, QueueIcon } from './Icons';
import styles from './MiniPlayer.module.css';

export default function MiniPlayer() {
  const navigate = useNavigate();
  const {
    currentTrack,
    isPlaying,
    isLoading,
    togglePlay,
    playNext,
    playPrevious,
    progress,
    duration
  } = usePlayer();

  if (!currentTrack) return null;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? (progress / duration) * 100 : 0;

  return (
    <div className={styles.miniPlayer}>
      <div className={styles.progress} style={{ width: `${progressPercent}%` }} />

      <div className={styles.content}>
        <div className={styles.trackInfo}>
          <div className={styles.coverWrapper}>
            <img
              src={currentTrack.cover || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23282828" width="100" height="100"/></svg>'}
              alt={currentTrack.title}
              className={`${styles.cover} ${isLoading ? styles.loading : ''}`}
            />
            {isLoading && (
              <div className={styles.loadingSpinner}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 2a10 10 0 0 1 10 10" />
                </svg>
              </div>
            )}
          </div>
          <div className={styles.text}>
            <div className={styles.title}>{currentTrack.title}</div>
            <div className={styles.artist}>{currentTrack.artist}</div>
          </div>
        </div>

        <div className={styles.controls}>
          <button className={styles.controlBtn} onClick={playPrevious}>
            <PrevIcon size={24} />
          </button>

          <button className={styles.playBtn} onClick={togglePlay} disabled={isLoading}>
            {isLoading ? (
              <div className={styles.playSpinner} />
            ) : isPlaying ? (
              <PauseIcon size={28} fill="#121212" />
            ) : (
              <PlayIcon size={28} fill="#121212" />
            )}
          </button>

          <button className={styles.controlBtn} onClick={playNext}>
            <NextIcon size={24} />
          </button>
          
          <button className={styles.controlBtn} onClick={() => navigate('/queue')}>
            <QueueIcon size={20} />
          </button>
        </div>

        <div className={styles.time}>
          {formatTime(progress)} / {formatTime(duration)}
        </div>
      </div>
    </div>
  );
}
