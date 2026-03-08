import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePlayer } from '../contexts/PlayerContext';
import { musicAPI } from '../api/musicApi';
import PageTransition from '../components/PageTransition';
import TrackCard from '../components/TrackCard';
import { BackIcon, PlayIcon, PauseIcon } from '../components/Icons';
import styles from './Album.module.css';

export default function Album() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { playTrack, currentTrack, isPlaying } = usePlayer();
  
  const [album, setAlbum] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadAlbum = async () => {
      if (!id) return;
      
      setIsLoading(true);
      setError(null);

      try {
        const [albumData, tracksData] = await Promise.all([
          musicAPI.getAlbum(id).catch(() => null),
          musicAPI.getAlbumTracks(id, 50).catch(() => ({ tracks: [] })),
        ]);

        if (!albumData) {
          setError('Альбом не найден');
          return;
        }

        setAlbum(albumData);
        setTracks(tracksData.tracks || albumData.tracks || []);
      } catch (err) {
        setError(err.message || 'Ошибка загрузки');
      } finally {
        setIsLoading(false);
      }
    };

    loadAlbum();
  }, [id]);

  const handlePlayAll = () => {
    if (tracks.length > 0) {
      playTrack(tracks[0], tracks);
    }
  };

  const handleTrackClick = (track) => {
    playTrack(track, tracks);
  };

  const isCurrentAlbum = () => {
    return currentTrack && tracks.some(t => t.id === currentTrack.id);
  };

  if (isLoading) {
    return (
      <PageTransition>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Загрузка...</p>
        </div>
      </PageTransition>
    );
  }

  if (error || !album) {
    return (
      <PageTransition>
        <div className={styles.error}>
          <p>⚠️ {error || 'Альбом не найден'}</p>
          <button onClick={() => navigate(-1)}>Назад</button>
        </div>
      </PageTransition>
    );
  }

  const albumArtist = album.artists?.[0]?.name || 'Various Artists';

  return (
    <PageTransition>
      <div className={styles.album}>
        {/* Header */}
        <div className={styles.header}>
          <button className={styles.backButton} onClick={() => navigate(-1)}>
            <BackIcon size={24} />
          </button>
          
          <div className={styles.content}>
            {album.cover ? (
              <img src={album.cover} alt={album.name} className={styles.cover} />
            ) : (
              <div className={styles.coverPlaceholder} />
            )}
            
            <div className={styles.info}>
              <span className={styles.type}>
                {album.album_type === 'single' ? 'Сингл' : 'Альбом'}
              </span>
              <h1 className={styles.name}>{album.name}</h1>
              
              <div className={styles.artists}>
                {album.artists?.map((artist, index) => (
                  <span key={artist.id || index}>
                    {index > 0 && ', '}
                    {artist.name}
                  </span>
                ))}
              </div>
              
              <div className={styles.meta}>
                {album.release_date && (
                  <span>{new Date(album.release_date).getFullYear()}</span>
                )}
                {tracks.length > 0 && (
                  <span>• {tracks.length} треков</span>
                )}
                {album.label && (
                  <span>• {album.label}</span>
                )}
              </div>
            </div>
          </div>
          
          <button 
            className={styles.playButton}
            onClick={handlePlayAll}
            disabled={tracks.length === 0}
          >
            {isCurrentAlbum() && isPlaying ? (
              <>
                <PauseIcon size={24} fill="#000" />
                <span>Пауза</span>
              </>
            ) : (
              <>
                <PlayIcon size={24} fill="#000" />
                <span>Слушать</span>
              </>
            )}
          </button>
        </div>

        {/* Треклист */}
        {tracks.length > 0 && (
          <section className={styles.tracklist}>
            {tracks.map((track, index) => {
              const isCurrent = currentTrack?.id === track.id;
              
              return (
                <div
                  key={track.id || index}
                  className={`${styles.trackRow} ${isCurrent ? styles.current : ''}`}
                  onClick={() => handleTrackClick(track)}
                >
                  <div className={styles.trackNumber}>
                    {isCurrent && isPlaying ? (
                      <div className={styles.equalizer}>
                        <div className={styles.bar}></div>
                        <div className={styles.bar}></div>
                        <div className={styles.bar}></div>
                      </div>
                    ) : (
                      index + 1
                    )}
                  </div>
                  
                  <div className={styles.trackInfo}>
                    <span className={styles.trackTitle}>{track.title}</span>
                    {track.artist && (
                      <span className={styles.trackArtist}>{track.artist}</span>
                    )}
                  </div>
                  
                  <div className={styles.trackDuration}>
                    {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                  </div>
                </div>
              );
            })}
          </section>
        )}

        <div className={styles.spacer} />
      </div>
    </PageTransition>
  );
}
