import React, { useContext, useState } from 'react';
import { PlayerContext } from '../contexts/PlayerContext';
import './Queue.css';

const Queue = () => {
  const { queue, currentTrack, playTrack, addToQueue, removeFromQueue, clearQueue } = useContext(PlayerContext);
  const [isExpanded, setIsExpanded] = useState(false);

  const handlePlayNow = (track, index) => {
    const newQueue = [...queue];
    const [removed] = newQueue.splice(index, 1);
    playTrack(removed, newQueue);
  };

  const handlePlayNext = (track, index) => {
    removeFromQueue(index);
    const newQueue = [track, ...queue];
    // В реальном приложении нужно обновить контекст
  };

  if (queue.length === 0 && !currentTrack) {
    return (
      <div className="queue">
        <div className="queue-placeholder">
          <svg viewBox="0 0 16 16" width="48" height="48">
            <path fill="currentColor" d="M15 15H1v-1.5h14V15zm0-4.5H1V9h14v1.5zm-14-7A2.5 2.5 0 0 1 3.5 1h9a2.5 2.5 0 0 1 2.5 2.5v1H1v-1z"/>
          </svg>
          <p>Очередь пуста</p>
          <span>Добавьте треки для воспроизведения</span>
        </div>
      </div>
    );
  }

  return (
    <div className="queue">
      <div className="queue-header">
        <h2 className="queue-title">Очередь</h2>
        <button className="clear-btn" onClick={clearQueue}>
          Очистить
        </button>
      </div>

      {currentTrack && (
        <div className="now-playing-section">
          <h3 className="section-label">Сейчас играет</h3>
          <div className="track-row now-playing">
            <div className="track-indicator">
              <div className="playing-bars">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <img src={currentTrack.cover} alt={currentTrack.title} className="track-cover" />
            <div className="track-info">
              <span className="track-name">{currentTrack.title}</span>
              <span className="track-artist">{currentTrack.artist}</span>
            </div>
            <span className="track-duration">
              {Math.floor(currentTrack.duration / 60)}:{(currentTrack.duration % 60).toString().padStart(2, '0')}
            </span>
          </div>
        </div>
      )}

      {queue.length > 0 && (
        <div className="queue-section">
          <h3 className="section-label">Далее ({queue.length})</h3>
          <div className="queue-list">
            {queue.map((track, index) => (
              <div 
                key={index} 
                className="track-row"
                onDragStart={(e) => e.dataTransfer.setData('text/plain', index)}
                draggable
              >
                <div className="track-number">{index + 1}</div>
                <img src={track.cover} alt={track.title} className="track-cover" />
                <div className="track-info">
                  <span className="track-name">{track.title}</span>
                  <span className="track-artist">{track.artist}</span>
                </div>
                <span className="track-duration">
                  {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                </span>
                <div className="track-actions">
                  <button 
                    className="action-btn play-next"
                    title="Играть следующим"
                    onClick={() => handlePlayNow(track, index)}
                  >
                    <svg viewBox="0 0 16 16" width="16" height="16">
                      <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
                    </svg>
                  </button>
                  <button 
                    className="action-btn remove"
                    title="Удалить из очереди"
                    onClick={() => removeFromQueue(index)}
                  >
                    <svg viewBox="0 0 16 16" width="16" height="16">
                      <path fill="currentColor" d="M2.5 1a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-11zm1 2a.5.5 0 0 0-.5.5V12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V3.5a.5.5 0 0 0-.5-.5h-9zM5 5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V5zm4 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V5z"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Queue;
