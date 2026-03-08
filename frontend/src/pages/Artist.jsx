import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePlayer } from '../contexts/PlayerContext';
import { musicAPI } from '../api/musicApi';
import PageTransition from '../components/PageTransition';
import TrackCard from '../components/TrackCard';
import AlbumCard from '../components/AlbumCard';
import { PlayIcon, BackIcon } from '../components/Icons';
import styles from './Artist.module.css';

export default function Artist() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { playTrack } = usePlayer();
  
  const [artist, setArtist] = useState(null);
  const [topTracks, setTopTracks] = useState([]);
  const [albums, setAlbums] = useState([]);
  const [singles, setSingles] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadArtist = async () => {
      if (!id) return;
      
      setIsLoading(true);
      setError(null);

      try {
        // Загружаем всё параллельно
        const [artistData, topTracksData, albumsData, recommendationsData] = await Promise.all([
          musicAPI.getArtist(id).catch(() => null),
          musicAPI.getArtistTopTracks(id, 10).catch(() => ({ tracks: [] })),
          musicAPI.getArtistAlbums(id, 'album,single', 20).catch(() => ({ albums: [] })),
          musicAPI.getArtistRecommendations(id, 20).catch(() => ({ tracks: [] })),
        ]);

        if (!artistData) {
          setError('Артист не найден');
          return;
        }

        setArtist(artistData);
        setTopTracks(topTracksData.tracks || []);
        
        // Разделяем альбомы и синглы
        const albumItems = (albumsData.albums || []).filter(a => a.album_type === 'album');
        const singleItems = (albumsData.albums || []).filter(a => a.album_type === 'single');
        setAlbums(albumItems);
        setSingles(singleItems);
        setRecommendations(recommendationsData.tracks || []);
      } catch (err) {
        setError(err.message || 'Ошибка загрузки');
      } finally {
        setIsLoading(false);
      }
    };

    loadArtist();
  }, [id]);

  const handlePlayAll = () => {
    if (topTracks.length > 0) {
      playTrack(topTracks[0], topTracks);
    }
  };

  const handleAlbumClick = (albumId) => {
    navigate(`/album/${albumId}`);
  };

  const handleTrackClick = (track, queue) => {
    playTrack(track, queue);
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

  if (error || !artist) {
    return (
      <PageTransition>
        <div className={styles.error}>
          <p>⚠️ {error || 'Артист не найден'}</p>
          <button onClick={() => navigate(-1)}>Назад</button>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className={styles.artist}>
        {/* Header с баннером */}
        <div className={styles.header}>
          <button className={styles.backButton} onClick={() => navigate(-1)}>
            <BackIcon size={24} />
          </button>
          
          <div className={styles.bannerContainer}>
            {artist.banner ? (
              <img src={artist.banner} alt={artist.name} className={styles.banner} />
            ) : (
              <div className={styles.bannerPlaceholder} />
            )}
            <div className={styles.bannerOverlay} />
          </div>
          
          <div className={styles.artistInfo}>
            {artist.cover && (
              <img src={artist.cover} alt={artist.name} className={styles.cover} />
            )}
            <h1 className={styles.name}>{artist.name}</h1>
            {artist.followers > 0 && (
              <p className={styles.followers}>
                {artist.followers.toLocaleString()} подписчиков
              </p>
            )}
            {artist.genres && artist.genres.length > 0 && (
              <div className={styles.genres}>
                {artist.genres.slice(0, 5).map(genre => (
                  <span key={genre} className={styles.genreTag}>{genre}</span>
                ))}
              </div>
            )}
          </div>
          
          <button className={styles.playButton} onClick={handlePlayAll}>
            <PlayIcon size={24} fill="#000" />
            <span>Слушать всё</span>
          </button>
        </div>

        {/* Популярные треки */}
        {topTracks.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Популярное</h2>
            <div className={styles.trackList}>
              {topTracks.map((track, index) => (
                <TrackCard
                  key={track.id}
                  track={track}
                  queue={topTracks}
                  onClick={() => handleTrackClick(track, topTracks)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Альбомы */}
        {albums.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Альбомы</h2>
            <div className={styles.horizontalScroll}>
              {albums.map(album => (
                <AlbumCard
                  key={album.id}
                  item={{
                    ...album,
                    type: 'album',
                    artist: artist.name
                  }}
                  onClick={() => handleAlbumClick(album.id)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Синглы */}
        {singles.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Синглы</h2>
            <div className={styles.horizontalScroll}>
              {singles.map(single => (
                <AlbumCard
                  key={single.id}
                  item={{
                    ...single,
                    type: 'single',
                    artist: artist.name
                  }}
                  onClick={() => handleAlbumClick(single.id)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Рекомендации */}
        {recommendations.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Похожие артисты</h2>
            <div className={styles.trackList}>
              {recommendations.map((track, index) => (
                <TrackCard
                  key={track.id}
                  track={track}
                  queue={recommendations}
                  onClick={() => handleTrackClick(track, recommendations)}
                />
              ))}
            </div>
          </section>
        )}

        <div className={styles.spacer} />
      </div>
    </PageTransition>
  );
}
