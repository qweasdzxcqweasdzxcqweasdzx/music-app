import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Library.css';

const Library = () => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [likedTracks, setLikedTracks] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [albums, setAlbums] = useState([]);
  const [artists, setArtists] = useState([]);

  const filters = [
    { id: 'all', label: 'Все', icon: 'grid' },
    { id: 'playlists', label: 'Плейлисты', icon: 'playlist' },
    { id: 'artists', label: 'Артисты', icon: 'artist' },
    { id: 'albums', label: 'Альбомы', icon: 'album' },
  ];

  useEffect(() => {
    // Загрузка любимых треков
    const liked = JSON.parse(localStorage.getItem('likedTracks') || '[]');
    setLikedTracks(liked);

    // Загрузка плейлистов
    const userPlaylists = JSON.parse(localStorage.getItem('playlists') || '[]');
    setPlaylists(userPlaylists);

    // Загрузка альбомов (из истории)
    const history = JSON.parse(localStorage.getItem('listeningHistory') || '[]');
    const uniqueAlbums = [];
    const albumIds = new Set();
    history.forEach(track => {
      if (track.album && !albumIds.has(track.album_id)) {
        albumIds.add(track.album_id);
        uniqueAlbums.push({
          id: track.album_id,
          title: track.album,
          artist: track.artist,
          cover: track.cover,
          year: new Date().getFullYear()
        });
      }
    });
    setAlbums(uniqueAlbums.slice(0, 20));

    // Загрузка артистов
    const uniqueArtists = [];
    const artistIds = new Set();
    history.forEach(track => {
      if (track.artist && !artistIds.has(track.artist)) {
        artistIds.add(track.artist);
        uniqueArtists.push({
          id: track.artist_id || track.artist,
          name: track.artist,
          cover: track.cover
        });
      }
    });
    setArtists(uniqueArtists.slice(0, 20));
  }, []);

  const getContent = () => {
    switch (activeFilter) {
      case 'playlists':
        return (
          <>
            <div className="library-header">
              <h1 className="library-title">Плейлисты</h1>
              <button className="create-playlist-btn">
                <svg viewBox="0 0 16 16" width="16" height="16">
                  <path fill="currentColor" d="M15.25 8a.75.75 0 0 1-.75.75H8.75v5.75a.75.75 0 0 1-1.5 0V8.75H1.5a.75.75 0 0 1 0-1.5h5.75V1.5a.75.75 0 0 1 1.5 0v5.75h5.75a.75.75 0 0 1 .75.75z"/>
                </svg>
                Создать плейлист
              </button>
            </div>
            
            <div className="playlists-grid">
              <Link to="/liked" className="playlist-card liked">
                <div className="playlist-cover">
                  <svg viewBox="0 0 16 16" width="48" height="48">
                    <path fill="#1ed760" d="M15.7244 6.1282C15.7244 10.0015 11.0613 14.0252 8.38299 15.8965C8.18146 16.0373 7.93649 16.1094 7.68999 16.1094C7.44349 16.1094 7.19852 16.0373 6.99699 15.8965C4.31869 14.0252 -0.344482 10.0015 -0.344482 6.1282C-0.344482 3.8762 1.49002 2.0417 3.74199 2.0417C5.06199 2.0417 6.23499 2.6732 6.99699 3.6212C7.37499 3.1512 8.00649 2.8617 8.68999 2.8617C9.82699 2.8617 10.751 3.7857 10.751 4.9227C10.751 5.0517 10.736 5.1767 10.7125 5.2977C12.783 5.6717 14.371 7.4812 14.371 9.6617C14.371 9.8417 14.351 10.0177 14.316 10.1897C15.141 9.4217 15.7244 8.5217 15.7244 7.5217V6.1282Z"/>
                  </svg>
                </div>
                <div className="playlist-info">
                  <span className="playlist-name">Любимые треки</span>
                  <span className="playlist-count">{likedTracks.length} треков</span>
                </div>
              </Link>

              {playlists.map((playlist, index) => (
                <Link key={index} to={`/playlist/${playlist.id}`} className="playlist-card">
                  <div className="playlist-cover">
                    <img src={playlist.cover || `https://picsum.photos/seed/${index}/300/300`} alt={playlist.name} />
                  </div>
                  <div className="playlist-info">
                    <span className="playlist-name">{playlist.name}</span>
                    <span className="playlist-count">{playlist.tracks?.length || 0} треков</span>
                  </div>
                </Link>
              ))}
            </div>
          </>
        );

      case 'artists':
        return (
          <>
            <h1 className="library-title">Артисты</h1>
            <div className="artists-grid-large">
              {artists.map((artist, index) => (
                <Link key={index} to={`/artist/${artist.id}`} className="artist-card-large">
                  <div className="artist-cover-large">
                    <img src={artist.cover} alt={artist.name} />
                  </div>
                  <span className="artist-name-large">{artist.name}</span>
                </Link>
              ))}
            </div>
          </>
        );

      case 'albums':
        return (
          <>
            <h1 className="library-title">Альбомы</h1>
            <div className="albums-grid">
              {albums.map((album, index) => (
                <Link key={index} to={`/album/${album.id}`} className="album-card">
                  <div className="album-cover">
                    <img src={album.cover} alt={album.title} />
                  </div>
                  <div className="album-info">
                    <span className="album-name">{album.title}</span>
                    <span className="album-artist">{album.artist}</span>
                  </div>
                </Link>
              ))}
            </div>
          </>
        );

      default:
        return (
          <>
            <h1 className="library-title">Моя медиатека</h1>
            
            <div className="library-stats">
              <div className="stat-card">
                <div className="stat-icon playlists">
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M15.25 8a.75.75 0 0 1-.75.75H8.75v5.75a.75.75 0 0 1-1.5 0V8.75H1.5a.75.75 0 0 1 0-1.5h5.75V1.5a.75.75 0 0 1 1.5 0v5.75h5.75a.75.75 0 0 1 .75.75z"/>
                  </svg>
                </div>
                <div className="stat-info">
                  <span className="stat-count">{playlists.length + 1}</span>
                  <span className="stat-label">Плейлистов</span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon artists">
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 1c-2 0-6 1-6 3v1h12v-1c0-2-4-3-6-3z"/>
                  </svg>
                </div>
                <div className="stat-info">
                  <span className="stat-count">{artists.length}</span>
                  <span className="stat-label">Артистов</span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon albums">
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/>
                  </svg>
                </div>
                <div className="stat-info">
                  <span className="stat-count">{albums.length}</span>
                  <span className="stat-label">Альбомов</span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon liked">
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M15.7244 6.1282C15.7244 10.0015 11.0613 14.0252 8.38299 15.8965C8.18146 16.0373 7.93649 16.1094 7.68999 16.1094C7.44349 16.1094 7.19852 16.0373 6.99699 15.8965C4.31869 14.0252 -0.344482 10.0015 -0.344482 6.1282C-0.344482 3.8762 1.49002 2.0417 3.74199 2.0417C5.06199 2.0417 6.23499 2.6732 6.99699 3.6212C7.37499 3.1512 8.00649 2.8617 8.68999 2.8617C9.82699 2.8617 10.751 3.7857 10.751 4.9227C10.751 5.0517 10.736 5.1767 10.7125 5.2977C12.783 5.6717 14.371 7.4812 14.371 9.6617C14.371 9.8417 14.351 10.0177 14.316 10.1897C15.141 9.4217 15.7244 8.5217 15.7244 7.5217V6.1282Z"/>
                  </svg>
                </div>
                <div className="stat-info">
                  <span className="stat-count">{likedTracks.length}</span>
                  <span className="stat-label">Любимых треков</span>
                </div>
              </div>
            </div>

            {likedTracks.length > 0 && (
              <section className="library-section">
                <h2 className="section-title">Недавно добавленные</h2>
                <div className="track-list">
                  {likedTracks.slice(0, 10).map((track, index) => (
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
          </>
        );
    }
  };

  return (
    <div className="library">
      <div className="library-filters">
        {filters.map((filter) => (
          <button
            key={filter.id}
            className={`filter-btn ${activeFilter === filter.id ? 'active' : ''}`}
            onClick={() => setActiveFilter(filter.id)}
          >
            {filter.label}
          </button>
        ))}
      </div>
      <div className="library-content">
        {getContent()}
      </div>
    </div>
  );
};

export default Library;
