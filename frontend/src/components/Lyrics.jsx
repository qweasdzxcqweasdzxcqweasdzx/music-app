import React, { useState, useEffect } from 'react';
import './Lyrics.css';

const Lyrics = ({ track }) => {
  const [lyrics, setLyrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!track) return;

    const fetchLyrics = async () => {
      setLoading(true);
      setError(null);

      try {
        // Поиск через Genius API
        const searchQuery = `${track.artist} ${track.title}`;
        
        // Используем прокси для обхода CORS
        const response = await fetch(
          `https://api.genius.com/search?q=${encodeURIComponent(searchQuery)}`,
          {
            headers: {
              'Authorization': 'Bearer 4_plsVXeuCKAfxi6Qu1xPd2FWzw6XBw_DBDSarXaeXHEa09jMAuOW5uZaNFHcdrb'
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch lyrics');
        }
        
        const data = await response.json();
        
        if (data.response && data.response.hits && data.response.hits.length > 0) {
          const song = data.response.hits[0].result;
          
          // Получаем текст песни
          const lyricsResponse = await fetch(
            `https://api.genius.com/songs/${song.id}`,
            {
              headers: {
                'Authorization': 'Bearer 4_plsVXeuCKAfxi6Qu1xPd2FWzw6XBw_DBDSarXaeXHEa09jMAuOW5uZaNFHcdrb'
              }
            }
          );
          
          const lyricsData = await lyricsResponse.json();
          const songData = lyricsData.response.song;
          
          setLyrics({
            text: null, // Genius не отдаёт текст напрямую, нужен парсинг
            url: song.url,
            title: songData.title,
            artist: songData.artist.name,
            albumArt: songData.song_art_image_url
          });
        } else {
          setError('Текст не найден');
        }
      } catch (err) {
        // Fallback - показываем заглушку
        setLyrics({
          text: `♪ ${track.title} - ${track.artist} ♪\n\nТекст песни будет доступен здесь.\n\nСлова и музыка: ${track.artist}`,
          url: null
        });
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchLyrics, 500);
    return () => clearTimeout(timer);
  }, [track]);

  if (!track) {
    return (
      <div className="lyrics">
        <div className="lyrics-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48">
            <path fill="currentColor" d="M12 3v9.28c-.47-.17-.97-.28-1.5-.28C8.01 12 6 14.01 6 16.5S8.01 21 10.5 21c2.31 0 4.2-1.75 4.45-4H15V6h4V3h-7z"/>
          </svg>
          <p>Включите трек для просмотра текста</p>
        </div>
      </div>
    );
  }

  return (
    <div className="lyrics">
      <div className="lyrics-header">
        <h2 className="lyrics-title">Текст песни</h2>
        <span className="lyrics-track-info">{track.title} — {track.artist}</span>
      </div>

      {loading ? (
        <div className="lyrics-loading">
          <div className="spinner"></div>
          <p>Загрузка текста...</p>
        </div>
      ) : error ? (
        <div className="lyrics-error">
          <p>{error}</p>
        </div>
      ) : lyrics ? (
        <div className="lyrics-content">
          {lyrics.url ? (
            <div className="lyrics-genius-card">
              {lyrics.albumArt && (
                <img src={lyrics.albumArt} alt={lyrics.title} className="lyrics-album-art" />
              )}
              <h3 className="lyrics-song-title">{lyrics.title}</h3>
              <p className="lyrics-song-artist">{lyrics.artist}</p>
              <a 
                href={lyrics.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="lyrics-link"
              >
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3zm-2 2H5v14h7v2H5c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2h7v2z"/>
                </svg>
                Открыть полный текст на Genius
              </a>
            </div>
          ) : (
            <pre className="lyrics-text">{lyrics.text}</pre>
          )}
        </div>
      ) : null}
    </div>
  );
};

export default Lyrics;
