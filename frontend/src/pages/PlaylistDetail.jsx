import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './PlaylistDetail.css';

const PlaylistDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [playlist, setPlaylist] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [draggedIndex, setDraggedIndex] = useState(null);

  useEffect(() => {
    // Загрузка плейлиста
    const playlists = JSON.parse(localStorage.getItem('playlists') || '[]');
    const found = playlists.find(p => p.id === id);
    
    if (id === 'liked') {
      const likedTracks = JSON.parse(localStorage.getItem('likedTracks') || '[]');
      setPlaylist({
        id: 'liked',
        name: 'Любимые треки',
        description: 'Все ваши любимые треки в одном месте',
        cover: null,
        tracks: likedTracks,
        isSystem: true
      });
    } else if (found) {
      setPlaylist(found);
      setEditName(found.name);
    } else {
      navigate('/library');
    }
  }, [id, navigate]);

  const handleSaveEdit = () => {
    if (!editName.trim()) return;
    
    const playlists = JSON.parse(localStorage.getItem('playlists') || '[]');
    const index = playlists.findIndex(p => p.id === id);
    if (index !== -1) {
      playlists[index].name = editName;
      localStorage.setItem('playlists', JSON.stringify(playlists));
      setPlaylist({ ...playlist, name: editName });
    }
    setIsEditing(false);
  };

  const handleDeleteTrack = (trackIndex) => {
    if (playlist.isSystem) return;
    
    const newTracks = playlist.tracks.filter((_, i) => i !== trackIndex);
    const updatedPlaylist = { ...playlist, tracks: newTracks };
    setPlaylist(updatedPlaylist);
    
    const playlists = JSON.parse(localStorage.getItem('playlists') || '[]');
    const index = playlists.findIndex(p => p.id === id);
    if (index !== -1) {
      playlists[index] = updatedPlaylist;
      localStorage.setItem('playlists', JSON.stringify(playlists));
    }
  };

  const handleDragStart = (e, index) => {
    if (playlist.isSystem) return;
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, index) => {
    if (playlist.isSystem || draggedIndex === null) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, dropIndex) => {
    if (playlist.isSystem || draggedIndex === null || draggedIndex === dropIndex) return;
    
    const newTracks = [...playlist.tracks];
    const [removed] = newTracks.splice(draggedIndex, 1);
    newTracks.splice(dropIndex, 0, removed);
    
    const updatedPlaylist = { ...playlist, tracks: newTracks };
    setPlaylist(updatedPlaylist);
    
    if (!playlist.isSystem) {
      const playlists = JSON.parse(localStorage.getItem('playlists') || '[]');
      const index = playlists.findIndex(p => p.id === id);
      if (index !== -1) {
        playlists[index] = updatedPlaylist;
        localStorage.setItem('playlists', JSON.stringify(playlists));
      }
    }
    
    setDraggedIndex(null);
  };

  if (!playlist) return null;

  const totalDuration = playlist.tracks.reduce((acc, t) => acc + (t.duration || 0), 0);
  const hours = Math.floor(totalDuration / 3600);
  const minutes = Math.floor((totalDuration % 3600) / 60);

  return (
    <div className="playlist-detail">
      <div className="playlist-header">
        <div className="playlist-cover-large" style={{
          background: playlist.isSystem 
            ? 'linear-gradient(135deg, #450af5, #c4efd9)' 
            : `url(${playlist.cover || `https://picsum.photos/seed/${id}/300/300`})`
        }}>
          {!playlist.cover && !playlist.isSystem && (
            <svg viewBox="0 0 16 16" width="64" height="64">
              <path fill="currentColor" d="M15.25 8a.75.75 0 0 1-.75.75H8.75v5.75a.75.75 0 0 1-1.5 0V8.75H1.5a.75.75 0 0 1 0-1.5h5.75V1.5a.75.75 0 0 1 1.5 0v5.75h5.75a.75.75 0 0 1 .75.75z"/>
            </svg>
          )}
        </div>
        <div className="playlist-info-large">
          <span className="playlist-type">Плейлист</span>
          {isEditing ? (
            <div className="edit-form">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onBlur={handleSaveEdit}
                onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit()}
                autoFocus
              />
            </div>
          ) : (
            <h1 className="playlist-title" onClick={() => !playlist.isSystem && setIsEditing(true)}>
              {playlist.name}
              {!playlist.isSystem && (
                <svg className="edit-icon" viewBox="0 0 16 16" width="16" height="16">
                  <path fill="currentColor" d="M11.013 1.427a1.75 1.75 0 0 1 2.474 0l1.086 1.086a1.75 1.75 0 0 1 0 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 0 1-.927-.928l.929-3.25c.081-.286.235-.547.445-.758l8.61-8.61zm.176 4.823L9.75 4.81l-6.286 6.287a.253.253 0 0 0-.064.108l-.558 1.953 1.953-.558a.253.253 0 0 0 .108-.064l6.286-6.286z"/>
                </svg>
              )}
            </h1>
          )}
          <p className="playlist-description">{playlist.description}</p>
          <div className="playlist-meta">
            <span className="meta-item">{playlist.tracks.length} треков</span>
            {hours > 0 && (
              <span className="meta-item">{hours} ч {minutes} мин</span>
            )}
            {hours === 0 && (
              <span className="meta-item">{minutes} мин</span>
            )}
          </div>
        </div>
      </div>

      <div className="playlist-controls">
        <button className="play-all-btn">
          <svg viewBox="0 0 16 16" width="24" height="24">
            <path fill="currentColor" d="M3 1.713a.7.7 0 0 1 1.05-.607l10.89 6.288a.7.7 0 0 1 0 1.212L4.05 14.894A.7.7 0 0 1 3 14.288V1.713z"/>
          </svg>
          {playlist.tracks.length > 0 ? 'Играть' : 'Плейлист пуст'}
        </button>
        {!playlist.isSystem && (
          <button className="add-track-btn">
            <svg viewBox="0 0 16 16" width="20" height="20">
              <path fill="currentColor" d="M15.25 8a.75.75 0 0 1-.75.75H8.75v5.75a.75.75 0 0 1-1.5 0V8.75H1.5a.75.75 0 0 1 0-1.5h5.75V1.5a.75.75 0 0 1 1.5 0v5.75h5.75a.75.75 0 0 1 .75.75z"/>
            </svg>
            Добавить треки
          </button>
        )}
      </div>

      <div className="playlist-tracks">
        <div className="tracks-header">
          <span className="header-number">#</span>
          <span className="header-title">Название</span>
          <span className="header-album">Альбом</span>
          <span className="header-date">Добавлен</span>
          <span className="header-duration">
            <svg viewBox="0 0 16 16" width="16" height="16">
              <path fill="currentColor" d="M8 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8z"/>
            </svg>
          </span>
        </div>

        {playlist.tracks.length === 0 ? (
          <div className="empty-playlist">
            <p>В этом плейлисте пока нет треков</p>
            <span>Добавьте треки из поиска или медиатеки</span>
          </div>
        ) : (
          playlist.tracks.map((track, index) => (
            <div
              key={index}
              className={`track-row ${draggedIndex === index ? 'dragging' : ''}`}
              draggable={!playlist.isSystem}
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDrop={(e) => handleDrop(e, index)}
            >
              <span className="track-number">
                {!playlist.isSystem && (
                  <svg className="drag-handle" viewBox="0 0 16 16" width="12" height="12">
                    <path fill="currentColor" d="M2 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 5a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm1 4a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm5-9a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 5a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 4a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm6-9a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 5a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 4a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
                  </svg>
                )}
                {index + 1}
              </span>
              <img src={track.cover} alt={track.title} className="track-cover" />
              <div className="track-info">
                <span className="track-title">{track.title}</span>
                <span className="track-artist">{track.artist}</span>
              </div>
              <span className="track-album">{track.album || '—'}</span>
              <span className="track-date">—</span>
              <span className="track-duration">
                {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
              </span>
              {!playlist.isSystem && (
                <button className="remove-btn" onClick={() => handleDeleteTrack(index)}>
                  <svg viewBox="0 0 16 16" width="16" height="16">
                    <path fill="currentColor" d="M2.5 1a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-11zm1 2a.5.5 0 0 0-.5.5V12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V3.5a.5.5 0 0 0-.5-.5h-9z"/>
                  </svg>
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default PlaylistDetail;
