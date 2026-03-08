import { useState, useEffect } from 'react';
import { usePlayer } from '../contexts/PlayerContext';
import { musicAPI } from '../api/musicApi';
import PageTransition from '../components/PageTransition';
import TrackCard from '../components/TrackCard';
import { BackIcon, QueueIcon, ClearIcon } from '../components/Icons';
import styles from './Queue.module.css';

export default function Queue() {
  const { queue, queueIndex, currentTrack, playTrack } = usePlayer();
  const [localQueue, setLocalQueue] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Загружаем очередь из API
  useEffect(() => {
    const loadQueue = async () => {
      try {
        const data = await musicAPI.getQueue();
        if (data && data.queue) {
          setLocalQueue(data.queue);
        }
      } catch (err) {
        console.error('Error loading queue:', err);
      }
    };
    
    loadQueue();
  }, []);

  const handleClearQueue = async () => {
    try {
      await musicAPI.clearQueue();
      setLocalQueue([]);
    } catch (err) {
      console.error('Error clearing queue:', err);
    }
  };

  const handleRemoveTrack = async (trackId) => {
    try {
      await musicAPI.removeFromQueue(trackId);
      setLocalQueue(prev => prev.filter(t => t.id !== trackId));
    } catch (err) {
      console.error('Error removing track:', err);
    }
  };

  const handlePlayTrack = (track, index) => {
    playTrack(track, localQueue);
  };

  // Объединяем локальную очередь с контекстом
  const displayQueue = localQueue.length > 0 ? localQueue : queue;

  return (
    <PageTransition>
      <div className={styles.queue}>
        <div className={styles.header}>
          <button className={styles.backButton} onClick={() => window.history.back()}>
            <BackIcon size={24} />
          </button>
          <h1 className={styles.title}>Очередь</h1>
          {displayQueue.length > 0 && (
            <button className={styles.clearButton} onClick={handleClearQueue}>
              <ClearIcon size={20} />
              <span>Очистить</span>
            </button>
          )}
        </div>

        {currentTrack && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Сейчас играет</h2>
            <div className={styles.currentTrack}>
              <img 
                src={currentTrack.cover || 'https://picsum.photos/seed/track/300/300'} 
                alt={currentTrack.title}
                className={styles.cover}
              />
              <div className={styles.info}>
                <div className={styles.title}>{currentTrack.title}</div>
                <div className={styles.artist}>{currentTrack.artist}</div>
              </div>
            </div>
          </section>
        )}

        {displayQueue.length > 0 ? (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <QueueIcon size={20} />
              Далее
            </h2>
            <div className={styles.trackList}>
              {displayQueue.map((track, index) => (
                <div 
                  key={track.id || index}
                  className={`${styles.trackRow} ${index === queueIndex ? styles.playing : ''}`}
                >
                  <div className={styles.trackContent} onClick={() => handlePlayTrack(track, index)}>
                    <img 
                      src={track.cover || 'https://picsum.photos/seed/track/100/100'} 
                      alt={track.title}
                      className={styles.trackCover}
                    />
                    <div className={styles.trackInfo}>
                      <div className={styles.trackTitle}>{track.title}</div>
                      <div className={styles.trackArtist}>{track.artist}</div>
                    </div>
                  </div>
                  <button 
                    className={styles.removeButton}
                    onClick={() => handleRemoveTrack(track.id)}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </section>
        ) : (
          <div className={styles.empty}>
            <QueueIcon size={48} />
            <p>Очередь пуста</p>
            <span>Добавьте треки для воспроизведения</span>
          </div>
        )}

        <div className={styles.spacer} />
      </div>
    </PageTransition>
  );
}
