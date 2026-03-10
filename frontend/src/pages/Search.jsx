import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Search.css';

const genreColors = [
  { id: 'pop', name: 'Pop', color: '#1DB954' },
  { id: 'rock', name: 'Rock', color: '#E91429' },
  { id: 'hiphop', name: 'Hip-Hop', color: '#DC148C' },
  { id: 'electronic', name: 'Electronic', color: '#0D73EC' },
  { id: 'indie', name: 'Indie', color: '#608108' },
  { id: 'metal', name: 'Metal', color: '#BC5900' },
  { id: 'jazz', name: 'Jazz', color: '#477D95' },
  { id: 'classical', name: 'Classical', color: '#8C67AC' },
  { id: 'rnb', name: 'R&B', color: '#DC143C' },
  { id: 'country', name: 'Country', color: '#5F4A3C' },
  { id: 'latin', name: 'Latin', color: '#E91E63' },
  { id: 'reggae', name: 'Reggae', color: '#009688' },
  { id: 'blues', name: 'Blues', color: '#3F51B5' },
  { id: 'soul', name: 'Soul', color: '#9C27B0' },
  { id: 'funk', name: 'Funk', color: '#FF5722' },
  { id: 'ambient', name: 'Ambient', color: '#00BCD4' },
  { id: 'house', name: 'House', color: '#FFC107' },
  { id: 'techno', name: 'Techno', color: '#607D8B' },
  { id: 'trance', name: 'Trance', color: '#9E9E9E' },
  { id: 'dubstep', name: 'Dubstep', color: '#795548' },
  { id: 'drum-and-bass', name: 'Drum & Bass', color: '#3E2723' },
  { id: 'kpop', name: 'K-Pop', color: '#FF4081' },
  { id: 'jpop', name: 'J-Pop', color: '#E040FB' },
  { id: 'focus', name: 'Focus', color: '#536DFE' },
];

const Search = () => {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState({ tracks: [], artists: [], albums: [] });
  const [isSearching, setIsSearching] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim()) {
        setIsSearching(true);
        fetch(`https://carrier-conservative-operations-enhancements.trycloudflare.com/api/search?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            setSearchResults(data);
            setIsSearching(false);
          })
          .catch(() => {
            setSearchResults({ tracks: [], artists: [], albums: [] });
            setIsSearching(false);
          });

        // Save to recent searches
        const saved = JSON.parse(localStorage.getItem('recentSearches') || '[]');
        if (!saved.includes(query)) {
          saved.unshift(query);
          localStorage.setItem('recentSearches', JSON.stringify(saved.slice(0, 10)));
          setRecentSearches(saved.slice(0, 10));
        }
      } else {
        setSearchResults({ tracks: [], artists: [], albums: [] });
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [query]);

  const clearRecentSearches = () => {
    localStorage.removeItem('recentSearches');
    setRecentSearches([]);
  };

  return (
    <div className="search">
      <div className="search-header">
        <div className="search-input-container">
          <svg className="search-icon" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M10.53 2a8.53 8.53 0 0 1 6.97 13.47l5.3 5.3-1.42 1.42-5.3-5.3A8.53 8.53 0 1 1 10.53 2m0 2a6.53 6.53 0 1 0 0 13.06 6.53 6.53 0 0 0 0-13.06z"/>
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Что хотите послушать?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      {query.trim() ? (
        <div className="search-results">
          {isSearching ? (
            <div className="search-loading">
              <div className="spinner"></div>
              <span>Поиск...</span>
            </div>
          ) : (
            <>
              {searchResults.tracks?.length > 0 && (
                <section className="search-section">
                  <h2 className="section-title">Треки</h2>
                  <div className="track-list">
                    {searchResults.tracks.slice(0, 10).map((track, index) => (
                      <div key={index} className="track-row">
                        <span className="track-number">{index + 1}</span>
                        <img src={track.cover} alt={track.title} className="track-image" />
                        <div className="track-info">
                          <span className="track-title">{track.title}</span>
                          <span className="track-artist">{track.artist}</span>
                        </div>
                        <span className="track-duration">{Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}</span>
                        <button className="track-play-btn">
                          <svg viewBox="0 0 16 16" width="16" height="16">
                            <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {searchResults.artists?.length > 0 && (
                <section className="search-section">
                  <h2 className="section-title">Артисты</h2>
                  <div className="artists-grid">
                    {searchResults.artists.slice(0, 6).map((artist, index) => (
                      <Link key={index} to={`/artist/${artist.id}`} className="artist-card">
                        <div className="artist-image">
                          <img src={artist.cover} alt={artist.name} />
                        </div>
                        <span className="artist-name">{artist.name}</span>
                      </Link>
                    ))}
                  </div>
                </section>
              )}

              {searchResults.albums?.length > 0 && (
                <section className="search-section">
                  <h2 className="section-title">Альбомы</h2>
                  <div className="cards-grid">
                    {searchResults.albums.slice(0, 6).map((album, index) => (
                      <Link key={index} to={`/album/${album.id}`} className="card">
                        <div className="card-image">
                          <img src={album.cover} alt={album.title} />
                          <button className="card-play-button">
                            <svg viewBox="0 0 16 16" width="24" height="24">
                              <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                            </svg>
                          </button>
                        </div>
                        <div className="card-title">{album.title}</div>
                        <div className="card-subtitle">{album.artist}</div>
                      </Link>
                    ))}
                  </div>
                </section>
              )}

              {searchResults.tracks?.length === 0 && searchResults.artists?.length === 0 && searchResults.albums?.length === 0 && (
                <div className="no-results">
                  <p>Ничего не найдено по запросу "{query}"</p>
                </div>
              )}
            </>
          )}
        </div>
      ) : (
        <div className="browse-section">
          <h2 className="browse-title">Все жанры</h2>
          <div className="genre-grid">
            {genreColors.map((genre) => (
              <Link
                key={genre.id}
                to={`/genre/${genre.id}`}
                className="genre-card"
                style={{ background: genre.color }}
              >
                <span className="genre-name">{genre.name}</span>
                <img
                  src={`https://picsum.photos/seed/${genre.id}/100/100`}
                  alt={genre.name}
                  className="genre-image"
                />
              </Link>
            ))}
          </div>

          {recentSearches.length > 0 && (
            <section className="recent-section">
              <div className="recent-header">
                <h2 className="recent-title">Недавние поисковые запросы</h2>
                <button className="clear-btn" onClick={clearRecentSearches}>
                  Очистить
                </button>
              </div>
              <div className="recent-chips">
                {recentSearches.map((search, index) => (
                  <button
                    key={index}
                    className="search-chip"
                    onClick={() => setQuery(search)}
                  >
                    {search}
                  </button>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
};

export default Search;
