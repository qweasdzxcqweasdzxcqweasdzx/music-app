import React, { useState, useRef, useEffect } from 'react';
import { musicAPI } from '../api/musicApi';
import './SimplePlayer.css';

const SimplePlayer = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [tracks, setTracks] = useState([]);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef(null);

  const searchTracks = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(
        `http://192.168.31.97:8000/api/censorship/search-uncensored?q=${encodeURIComponent(searchQuery)}&limit=10&prefer_explicit=true`
      );
      const data = await response.json();
      setTracks(data.tracks || []);
    } catch (error) {
      console.error('Search error:', error);
      setTracks([]);
    }
    setIsLoading(false);
  };

  const playTrack = async (track) => {
    try {
      // Извлекаем video_id из stream_url
      const videoId = extractVideoId(track.stream_url);
      
      if (!videoId) {
        console.error('No video ID found');
        return;
      }

      const streamUrl = `http://192.168.31.97:8000/audio/proxy/${videoId}`;
      
      setCurrentTrack({ ...track, streamUrl });
      
      if (audioRef.current) {
        audioRef.current.src = streamUrl;
        audioRef.current.load();
        audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Play error:', error);
    }
  };

  const extractVideoId = (url) => {
    if (!url) return null;
    const match = url.match(/(?:youtu\.be\/|youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  };

  const togglePlay = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      // Можно добавить обновление прогресс бара
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    // Автопереключение на следующий трек
    const currentIndex = tracks.findIndex(t => t.track._id === currentTrack?._id);
    if (currentIndex < tracks.length - 1) {
      playTrack(tracks[currentIndex + 1].track);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchTracks();
    }
  };

  return (
    <div className="simple-player">
      <div className="player-header">
        <h1>🎵 Music Player</h1>
      </div>

      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Поиск треков..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="search-button" onClick={searchTracks} disabled={isLoading}>
          {isLoading ? '🔍...' : '🔍 Найти'}
        </button>
      </div>

      <div className="tracks-list">
        {tracks.map((item, index) => {
          const track = item.track;
          return (
            <div
              key={index}
              className={`track-item ${currentTrack?._id === track._id ? 'active' : ''}`}
              onClick={() => playTrack(track)}
            >
              <div className="track-info">
                <div className="track-number">{index + 1}</div>
                <div className="track-details">
                  <div className="track-title">{track.title || 'Unknown'}</div>
                  <div className="track-artist">{track.artist || 'Unknown Artist'}</div>
                </div>
              </div>
              <div className="track-play">
                {currentTrack?._id === track._id && isPlaying ? '▶ Playing' : '▷ Play'}
              </div>
            </div>
          );
        })}
      </div>

      {currentTrack && (
        <div className="player-footer">
          <div className="now-playing">
            <div className="now-playing-info">
              <div className="now-playing-title">🎵 {currentTrack.title}</div>
              <div className="now-playing-artist">{currentTrack.artist}</div>
            </div>
            <button className="play-pause-button" onClick={togglePlay}>
              {isPlaying ? '⏸ Pause' : '▶ Play'}
            </button>
          </div>
          <audio
            ref={audioRef}
            onTimeUpdate={handleTimeUpdate}
            onEnded={handleEnded}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
        </div>
      )}
    </div>
  );
};

export default SimplePlayer;
