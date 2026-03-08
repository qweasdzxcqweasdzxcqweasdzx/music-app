import { PlayIcon } from './Icons';
import { useContext } from 'react';
import { PlayerContext } from '../contexts/PlayerContext';
import { useNavigate } from 'react-router-dom';
import styles from './TrackCard.module.css';

export default function TrackCard({ track, queue = [] }) {
  const navigate = useNavigate();
  const { playTrack, currentTrack, isPlaying } = useContext(PlayerContext)();
  const isCurrentTrack = currentTrack?.id === track.id;

  const handlePlay = () => {
    if (isCurrentTrack) {
      // Если это текущий трек - ничего не делаем
      return;
    }
    playTrack(track, queue.length > 0 ? queue : [track]);
  };

  const handleArtistClick = (e) => {
    e.stopPropagation();
    // Генерируем slug из имени артиста
    const slug = track.artist.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    navigate(`/artist/${slug || 'default'}`);
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className={`${styles.card} ${isCurrentTrack ? styles.active : ''}`}
      onClick={handlePlay}
    >
      <div className={styles.coverWrapper}>
        <img
          src={track.cover || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23282828" width="100" height="100"/></svg>'}
          alt={track.title}
          className={styles.cover}
        />
        <div className={`${styles.playOverlay} ${isCurrentTrack && isPlaying ? styles.playing : ''}`}>
          <PlayIcon size={24} fill="#121212" />
        </div>
      </div>

      <div className={styles.info}>
        <div className={styles.title}>{track.title}</div>
        <div 
          className={`${styles.artist} ${styles.artistLink}`}
          onClick={handleArtistClick}
        >
          {track.artist}
        </div>
      </div>

      <div className={styles.duration}>
        {formatDuration(track.duration || 180)}
      </div>
    </div>
  );
}
