import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { musicAPI } from '../api/musicApi';
import './Home.module.css';

const Home = () => {
  const navigate = useNavigate();
  const [greeting, setGreeting] = useState('Добрый вечер');
  const [recentTracks, setRecentTracks] = useState([]);
  const [trendingTracks, setTrendingTracks] = useState([]);
  const [featuredPlaylists, setFeaturedPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) setGreeting('Доброе утро');
    else if (hour >= 12 && hour < 18) setGreeting('Добрый день');
    else setGreeting('Добрый вечер');

    // Загрузка недавних треков
    const history = JSON.parse(localStorage.getItem('listeningHistory') || '[]');
    setRecentTracks(history.slice(0, 6).reverse());

    // Загрузка данных
    const loadData = async () => {
      try {
        const [trending, genres] = await Promise.allSettled([
          musicAPI.getTopTracks(10),
          musicAPI.getGenres()
        ]);

        if (trending.status === 'fulfilled') {
          setTrendingTracks(trending.value.tracks || []);
        } else {
          console.warn('Failed to load trending tracks:', trending.error);
        }

        // Плейлисты по жанрам
        if (genres.status === 'fulfilled') {
          const genreList = genres.value.genres || [];
          setFeaturedPlaylists(genreList.slice(0, 6).map(g => ({
            id: g.id,
            title: g.name,
            description: g.description,
            cover: `https://picsum.photos/seed/${g.id}/300/300`,
            type: 'genre'
          })));
        }
      } catch (error) {
        console.error('Error loading home data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handlePlayTrack = (track) => {
    // Сохраняем в историю
    const history = JSON.parse(localStorage.getItem('listeningHistory') || '[]');
    history.push({ ...track, playedAt: new Date().toISOString() });
    localStorage.setItem('listeningHistory', history.slice(-100));

    // Отправляем событие плееру
    window.dispatchEvent(new CustomEvent('play-track', { detail: track }));
  };

  const getGreetingGradient = () => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'linear-gradient(135deg, #1e3a5f, #0d73ec)';
    if (hour >= 12 && hour < 18) return 'linear-gradient(135deg, #1e5f3a, #1ed760)';
    return 'linear-gradient(135deg, #5f1e3a, #dc148c)';
  };

  if (loading) {
    return (
      <div className="home-loading">
        <div className="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>
    );
  }

  return (
    <div className="home">
      {/* Приветствие */}
      <div className="home-header" style={{ background: getGreetingGradient() }}>
        <h1 className="greeting">{greeting}</h1>
      </div>

      {/* Недавно прослушанные */}
      {recentTracks.length > 0 && (
        <section className="home-section">
          <div className="section-header">
            <h2 className="section-title">Недавно прослушанные</h2>
            <Link to="/library" className="section-link">Все</Link>
          </div>
          <div className="cards-grid">
            {recentTracks.map((track, index) => (
              <div 
                key={index} 
                className="card"
                onClick={() => handlePlayTrack(track)}
              >
                <div className="card-image">
                  <img 
                    src={track.cover || track.artwork_url || 'https://via.placeholder.com/300'} 
                    alt={track.title}
                    loading="lazy"
                  />
                  <button className="card-play-button">
                    <svg viewBox="0 0 16 16" width="24" height="24">
                      <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                    </svg>
                  </button>
                </div>
                <div className="card-title">{track.title}</div>
                <div className="card-subtitle">{track.artist}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Плейлисты */}
      {featuredPlaylists.length > 0 && (
        <section className="home-section">
          <div className="section-header">
            <h2 className="section-title">Популярные плейлисты</h2>
            <Link to="/search" className="section-link">Все</Link>
          </div>
          <div className="cards-grid">
            {featuredPlaylists.map((playlist, index) => (
              <div
                key={index}
                className="card"
                onClick={() => {
                  if (playlist.type === 'genre') {
                    navigate(`/genre/${playlist.id}`);
                  } else {
                    navigate(`/playlist/${playlist.id}`);
                  }
                }}
              >
                <div className="card-image">
                  <img 
                    src={playlist.cover || playlist.artwork_url || 'https://via.placeholder.com/300'} 
                    alt={playlist.title}
                    loading="lazy"
                  />
                  <button className="card-play-button">
                    <svg viewBox="0 0 16 16" width="24" height="24">
                      <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                    </svg>
                  </button>
                </div>
                <div className="card-title">{playlist.title}</div>
                <div className="card-subtitle">
                  {playlist.description || `${playlist.track_count || playlist.tracks_count} треков`}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Тренды */}
      <section className="home-section">
        <div className="section-header">
          <h2 className="section-title">Тренды SoundCloud</h2>
          <Link to="/search" className="section-link">Все</Link>
        </div>
        <div className="track-list">
          {trendingTracks.slice(0, 10).map((track, index) => (
            <div 
              key={index} 
              className="track-row"
              onClick={() => handlePlayTrack(track)}
            >
              <span className="track-number">{index + 1}</span>
              <img 
                src={track.cover || track.artwork_url || 'https://via.placeholder.com/60'} 
                alt={track.title}
                className="track-image"
                loading="lazy"
              />
              <div className="track-info">
                <span className="track-title">{track.title}</span>
                <span className="track-artist">{track.artist || track.user?.username}</span>
              </div>
              <span className="track-duration">
                {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
              </span>
              <button className="track-play-btn">
                <svg viewBox="0 0 16 16" width="16" height="16">
                  <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                </svg>
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
