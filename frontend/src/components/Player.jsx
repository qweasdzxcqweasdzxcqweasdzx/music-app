import React, { useContext, useState, useEffect } from 'react';
import { PlayerContext } from '../contexts/PlayerContext';
import { useNavigate } from 'react-router-dom';
import './Player.css';

const Player = () => {
  const { currentTrack, isPlaying, togglePlay, nextTrack, prevTrack, progress, duration, volume, setVolume, queue } = useContext(PlayerContext);
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isShuffle, setIsShuffle] = useState(false);
  const [repeatMode, setRepeatMode] = useState('off'); // off, all, one
  const [isLiked, setIsLiked] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (currentTrack) {
      const liked = JSON.parse(localStorage.getItem('likedTracks') || '[]');
      setIsLiked(liked.some(t => t._id === currentTrack._id));
    }
  }, [currentTrack]);

  const toggleLike = () => {
    if (!currentTrack) return;
    const liked = JSON.parse(localStorage.getItem('likedTracks') || '[]');
    if (isLiked) {
      localStorage.setItem('likedTracks', JSON.stringify(liked.filter(t => t._id !== currentTrack._id)));
    } else {
      localStorage.setItem('likedTracks', JSON.stringify([...liked, currentTrack]));
    }
    setIsLiked(!isLiked);
  };

  const toggleRepeat = () => {
    const modes = ['off', 'all', 'one'];
    const currentIndex = modes.indexOf(repeatMode);
    setRepeatMode(modes[(currentIndex + 1) % modes.length]);
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!currentTrack) {
    return (
      <div className="player">
        <div className="player-left">
          <div className="now-playing-placeholder">
            <span>Выберите трек для воспроизведения</span>
          </div>
        </div>
        <div className="player-center"></div>
        <div className="player-right"></div>
      </div>
    );
  }

  return (
    <>
      <div className="player">
        <div className="player-left">
          <div className="now-playing">
            <img 
              src={currentTrack.cover} 
              alt={currentTrack.title}
              className="now-playing-cover"
              onClick={() => setIsExpanded(true)}
            />
            <div className="now-playing-info" onClick={() => setIsExpanded(true)}>
              <span className="now-playing-title">{currentTrack.title}</span>
              <span className="now-playing-artist">{currentTrack.artist}</span>
            </div>
            <button 
              className={`like-btn ${isLiked ? 'active' : ''}`}
              onClick={toggleLike}
              aria-label={isLiked ? 'Удалить из любимых' : 'Добавить в любимые'}
            >
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M15.7244 6.1282C15.7244 10.0015 11.0613 14.0252 8.38299 15.8965C8.18146 16.0373 7.93649 16.1094 7.68999 16.1094C7.44349 16.1094 7.19852 16.0373 6.99699 15.8965C4.31869 14.0252 -0.344482 10.0015 -0.344482 6.1282C-0.344482 3.8762 1.49002 2.0417 3.74199 2.0417C5.06199 2.0417 6.23499 2.6732 6.99699 3.6212C7.37499 3.1512 8.00649 2.8617 8.68999 2.8617C9.82699 2.8617 10.751 3.7857 10.751 4.9227C10.751 5.0517 10.736 5.1767 10.7125 5.2977C12.783 5.6717 14.371 7.4812 14.371 9.6617C14.371 9.8417 14.351 10.0177 14.316 10.1897C15.141 9.4217 15.7244 8.5217 15.7244 7.5217V6.1282Z"/>
              </svg>
            </button>
          </div>
        </div>

        <div className="player-center">
          <div className="player-controls">
            <button 
              className={`control-btn shuffle ${isShuffle ? 'active' : ''}`}
              onClick={() => setIsShuffle(!isShuffle)}
              aria-label="Перемешать"
            >
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M13.151.922a.75.75 0 1 0-1.06 1.06L13.109 3H11.16a3.75 3.75 0 0 0-2.873 1.34l-6.173 7.356A2.25 2.25 0 0 1 .39 12.5H0V14h.391a3.75 3.75 0 0 0 2.873-1.34l6.173-7.356a2.25 2.25 0 0 1 1.724-.804h1.947l-1.017 1.018a.75.75 0 0 0 1.06 1.06L15.98 3.75 13.15.922zM.391 3.5H0V2h.391c1.109 0 2.16.49 2.873 1.34L4.89 5.277l-.979 1.167-1.796-2.14A2.25 2.25 0 0 0 .39 3.5z"/>
                <path fill="currentColor" d="m7.5 10.723.98-1.167.957 1.14a2.25 2.25 0 0 0 1.724.804h1.947l-1.017-1.018a.75.75 0 1 1 1.06-1.06l2.829 2.828-2.829 2.828a.75.75 0 1 1-1.06-1.06L13.109 13H11.16a3.75 3.75 0 0 1-2.873-1.34l-.787-.938z"/>
              </svg>
            </button>
            <button className="control-btn" onClick={prevTrack} aria-label="Предыдущий">
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M3.3 1a.7.7 0 0 1 .7.7v5.15l9.95-5.744a.7.7 0 0 1 1.05.606v12.575a.7.7 0 0 1-1.05.607L4 9.149V14.3a.7.7 0 0 1-.7.7H1.7a.7.7 0 0 1-.7-.7V1.7a.7.7 0 0 1 .7-.7h1.6z"/>
              </svg>
            </button>
            <button className="control-btn play-btn" onClick={togglePlay} aria-label={isPlaying ? 'Пауза' : 'Воспроизвести'}>
              {isPlaying ? (
                <svg viewBox="0 0 16 16" width="24" height="24">
                  <path fill="currentColor" d="M2.7 1a.7.7 0 0 0-.7.7v12.6a.7.7 0 0 0 .7.7h2.6a.7.7 0 0 0 .7-.7V1.7a.7.7 0 0 0-.7-.7H2.7zm8 0a.7.7 0 0 0-.7.7v12.6a.7.7 0 0 0 .7.7h2.6a.7.7 0 0 0 .7-.7V1.7a.7.7 0 0 0-.7-.7h-2.6z"/>
                </svg>
              ) : (
                <svg viewBox="0 0 16 16" width="24" height="24">
                  <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                </svg>
              )}
            </button>
            <button className="control-btn" onClick={nextTrack} aria-label="Следующий">
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M12.7 1a.7.7 0 0 0-.7.7v5.15L2.05 1.107A.7.7 0 0 0 1 1.712v12.575a.7.7 0 0 0 1.05.607L12 9.149V14.3a.7.7 0 0 0 .7.7h1.6a.7.7 0 0 0 .7-.7V1.7a.7.7 0 0 0-.7-.7h-1.6z"/>
              </svg>
            </button>
            <button 
              className={`control-btn repeat ${repeatMode !== 'off' ? 'active' : ''}`}
              onClick={toggleRepeat}
              aria-label="Повтор"
            >
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M0 4.75A3.75 3.75 0 0 1 3.75 1h8.5A3.75 3.75 0 0 1 16 4.75v5a3.75 3.75 0 0 1-3.75 3.75H9.81l1.018 1.018a.75.75 0 1 1-1.06 1.06L6.939 12.75l2.829-2.829a.75.75 0 1 1 1.06 1.06L9.81 12h2.44a2.25 2.25 0 0 0 2.25-2.25v-5a2.25 2.25 0 0 0-2.25-2.25h-8.5a2.25 2.25 0 0 0-2.25 2.25v5c0 .414.336.75.75.75s.75-.336.75-.75v-5z"/>
              </svg>
              {repeatMode === 'one' && (
                <span className="repeat-mode">1</span>
              )}
            </button>
          </div>

          <div className="playback-bar">
            <span className="time">{formatTime(progress)}</span>
            <div className="progress-container">
              <input
                type="range"
                min="0"
                max={duration || 100}
                value={progress || 0}
                className="progress-bar"
                style={{ '--progress': `${(progress / (duration || 100)) * 100}%` }}
                onChange={(e) => {
                  const audio = document.querySelector('audio');
                  if (audio) {
                    audio.currentTime = e.target.value;
                  }
                }}
              />
            </div>
            <span className="time">{formatTime(duration)}</span>
          </div>
        </div>

        <div className="player-right">
          <div className="volume-controls">
            <button className="control-btn" aria-label="Громкость">
              <svg viewBox="0 0 16 16" width="16" height="16">
                {volume === 0 ? (
                  <path fill="currentColor" d="M13.86 5.47a.75.75 0 0 0-1.061 0l-1.47 1.47-1.47-1.47A.75.75 0 0 0 8.8 6.53L10.269 8l-1.47 1.47a.75.75 0 1 0 1.06 1.06l1.47-1.47 1.47 1.47a.75.75 0 0 0 1.06-1.06L12.38 8l1.47-1.47a.75.75 0 0 0 0-1.06zM7.53 2.22a.75.75 0 0 0-1.06 0L3.53 5.17H1.75A.75.75 0 0 0 1 5.92v4.16a.75.75 0 0 0 .75.75h1.78l2.94 2.95a.75.75 0 0 0 1.06 0 .75.75 0 0 0 0-1.06L4.81 10V6l2.72-2.72a.75.75 0 0 0 0-1.06z"/>
                ) : volume < 0.5 ? (
                  <path fill="currentColor" d="M9.741.85a.75.75 0 0 1 .375.65v13a.75.75 0 0 1-1.125.65l-3.766-2.15H1.75A.75.75 0 0 1 1 12.25V3.75a.75.75 0 0 1 .75-.75h3.475l3.766-2.15a.75.75 0 0 1 .75 0zM6.5 11.25V4.75L3.75 6.31v3.38l2.75 1.56z"/>
                ) : (
                  <path fill="currentColor" d="M9.741.85a.75.75 0 0 1 .375.65v13a.75.75 0 0 1-1.125.65l-3.766-2.15H1.75A.75.75 0 0 1 1 12.25V3.75a.75.75 0 0 1 .75-.75h3.475l3.766-2.15a.75.75 0 0 1 .75 0zM6.5 11.25V4.75L3.75 6.31v3.38l2.75 1.56zm5.219 2.023a.75.75 0 0 1-1.06-1.06A5.48 5.48 0 0 0 12 8a5.48 5.48 0 0 0-1.34-4.213.75.75 0 1 1 1.06-1.06 7 7 0 0 1 0 9.146z"/>
                )}
              </svg>
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              className="volume-slider"
              onChange={(e) => {
                const audio = document.querySelector('audio');
                if (audio) {
                  audio.volume = e.target.value;
                }
              }}
            />
            <button 
              className="control-btn queue-btn" 
              aria-label="Очередь"
              onClick={() => navigate('/queue')}
            >
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M15 15H1v-1.5h14V15zm0-4.5H1V9h14v1.5zm-14-7A2.5 2.5 0 0 1 3.5 1h9a2.5 2.5 0 0 1 2.5 2.5v1H1v-1z"/>
              </svg>
              {queue.length > 0 && <span className="queue-count">{queue.length}</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Player Modal */}
      {isExpanded && (
        <div className="player-modal-overlay" onClick={() => setIsExpanded(false)}>
          <div className="player-modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setIsExpanded(false)}>
              <svg viewBox="0 0 16 16" width="24" height="24">
                <path fill="currentColor" d="M3.478 3.478a.75.75 0 0 1 1.06 0L8 6.94l3.462-3.462a.75.75 0 1 1 1.06 1.06L9.06 8l3.462 3.462a.75.75 0 1 1-1.06 1.06L8 9.06l-3.462 3.462a.75.75 0 0 1-1.06-1.06L6.94 8 3.478 4.538a.75.75 0 0 1 0-1.06z"/>
              </svg>
            </button>
            
            <div className="modal-content">
              <img src={currentTrack.cover} alt={currentTrack.title} className="modal-cover" />
              <div className="modal-info">
                <h2 className="modal-title">{currentTrack.title}</h2>
                <p className="modal-artist">{currentTrack.artist}</p>
              </div>

              <div className="modal-progress">
                <span>{formatTime(progress)}</span>
                <div className="modal-progress-bar">
                  <input
                    type="range"
                    min="0"
                    max={duration || 100}
                    value={progress || 0}
                    className="progress-bar"
                    style={{ '--progress': `${(progress / (duration || 100)) * 100}%` }}
                  />
                </div>
                <span>{formatTime(duration)}</span>
              </div>

              <div className="modal-controls">
                <button className={`control-btn large ${isShuffle ? 'active' : ''}`} onClick={() => setIsShuffle(!isShuffle)}>
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M13.151.922a.75.75 0 1 0-1.06 1.06L13.109 3H11.16a3.75 3.75 0 0 0-2.873 1.34l-6.173 7.356A2.25 2.25 0 0 1 .39 12.5H0V14h.391a3.75 3.75 0 0 0 2.873-1.34l6.173-7.356a2.25 2.25 0 0 1 1.724-.804h1.947l-1.017 1.018a.75.75 0 0 0 1.06 1.06L15.98 3.75 13.15.922zM.391 3.5H0V2h.391c1.109 0 2.16.49 2.873 1.34L4.89 5.277l-.979 1.167-1.796-2.14A2.25 2.25 0 0 0 .39 3.5z"/>
                  </svg>
                </button>
                <button className="control-btn large" onClick={prevTrack}>
                  <svg viewBox="0 0 16 16" width="28" height="28">
                    <path fill="currentColor" d="M3.3 1a.7.7 0 0 1 .7.7v5.15l9.95-5.744a.7.7 0 0 1 1.05.606v12.575a.7.7 0 0 1-1.05.607L4 9.149V14.3a.7.7 0 0 1-.7.7H1.7a.7.7 0 0 1-.7-.7V1.7a.7.7 0 0 1 .7-.7h1.6z"/>
                  </svg>
                </button>
                <button className="control-btn large play-btn" onClick={togglePlay}>
                  {isPlaying ? (
                    <svg viewBox="0 0 16 16" width="32" height="32">
                      <path fill="currentColor" d="M2.7 1a.7.7 0 0 0-.7.7v12.6a.7.7 0 0 0 .7.7h2.6a.7.7 0 0 0 .7-.7V1.7a.7.7 0 0 0-.7-.7H2.7zm8 0a.7.7 0 0 0-.7.7v12.6a.7.7 0 0 0 .7.7h2.6a.7.7 0 0 0 .7-.7V1.7a.7.7 0 0 0-.7-.7h-2.6z"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 16 16" width="32" height="32">
                      <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                    </svg>
                  )}
                </button>
                <button className="control-btn large" onClick={nextTrack}>
                  <svg viewBox="0 0 16 16" width="28" height="28">
                    <path fill="currentColor" d="M12.7 1a.7.7 0 0 0-.7.7v5.15L2.05 1.107A.7.7 0 0 0 1 1.712v12.575a.7.7 0 0 0 1.05.607L12 9.149V14.3a.7.7 0 0 0 .7.7h1.6a.7.7 0 0 0 .7-.7V1.7a.7.7 0 0 0-.7-.7h-1.6z"/>
                  </svg>
                </button>
                <button className={`control-btn large ${repeatMode !== 'off' ? 'active' : ''}`} onClick={toggleRepeat}>
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M0 4.75A3.75 3.75 0 0 1 3.75 1h8.5A3.75 3.75 0 0 1 16 4.75v5a3.75 3.75 0 0 1-3.75 3.75H9.81l1.018 1.018a.75.75 0 1 1-1.06 1.06L6.939 12.75l2.829-2.829a.75.75 0 1 1 1.06 1.06L9.81 12h2.44a2.25 2.25 0 0 0 2.25-2.25v-5a2.25 2.25 0 0 0-2.25-2.25h-8.5a2.25 2.25 0 0 0-2.25 2.25v5c0 .414.336.75.75.75s.75-.336.75-.75v-5z"/>
                  </svg>
                </button>
              </div>

              <div className="modal-actions">
                <button className={`action-btn ${isLiked ? 'active' : ''}`} onClick={toggleLike}>
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M15.7244 6.1282C15.7244 10.0015 11.0613 14.0252 8.38299 15.8965C8.18146 16.0373 7.93649 16.1094 7.68999 16.1094C7.44349 16.1094 7.19852 16.0373 6.99699 15.8965C4.31869 14.0252 -0.344482 10.0015 -0.344482 6.1282C-0.344482 3.8762 1.49002 2.0417 3.74199 2.0417C5.06199 2.0417 6.23499 2.6732 6.99699 3.6212C7.37499 3.1512 8.00649 2.8617 8.68999 2.8617C9.82699 2.8617 10.751 3.7857 10.751 4.9227C10.751 5.0517 10.736 5.1767 10.7125 5.2977C12.783 5.6717 14.371 7.4812 14.371 9.6617C14.371 9.8417 14.351 10.0177 14.316 10.1897C15.141 9.4217 15.7244 8.5217 15.7244 7.5217V6.1282Z"/>
                  </svg>
                </button>
                <button className="action-btn">
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M8 0a.75.75 0 0 1 .75.75v5.5l3.72 2.15a.75.75 0 0 1-.75 1.3L8 7.52 4.28 9.7a.75.75 0 0 1-.75-1.3L7.25 6.25V.75A.75.75 0 0 1 8 0zM1.676 4.33a.75.75 0 0 1 1.015-.273l5.31 3.07v9.123a.75.75 0 0 1-1.5 0V7.98l-4.55-2.636a.75.75 0 0 1-.274-1.015zm12.648 0a.75.75 0 0 1-.274 1.015l-4.55 2.637v8.268a.75.75 0 0 1-1.5 0V7.128l5.31-3.07a.75.75 0 0 1 1.014.272z"/>
                  </svg>
                </button>
                <button className="action-btn">
                  <svg viewBox="0 0 16 16" width="24" height="24">
                    <path fill="currentColor" d="M8 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8z"/>
                    <circle cx="8" cy="8" r="1.5" fill="currentColor"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Player;
