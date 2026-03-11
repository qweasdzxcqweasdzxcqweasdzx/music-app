import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './CensoredTracks.module.css';

const API_BASE = '/api/censored-tracks';

const CensoredTracks = () => {
  const [tracks, setTracks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTrack, setNewTrack] = useState({
    title: '',
    artist: '',
    platform: 'soundcloud',
    platform_id: '',
    censorship_type: 'clean_version',
    description: '',
  });

  // Загрузка данных
  useEffect(() => {
    loadTracks();
    loadStats();
  }, [filter]);

  const loadTracks = async () => {
    setLoading(true);
    try {
      const statusParam = filter === 'all' ? '' : `&status=${filter}`;
      const response = await fetch(`${API_BASE}/search?limit=100${statusParam}`);
      const data = await response.json();
      setTracks(data);
    } catch (error) {
      console.error('Error loading tracks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  // Добавление трека
  const handleAddTrack = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTrack),
      });
      
      if (response.ok) {
        await loadTracks();
        await loadStats();
        setShowAddForm(false);
        setNewTrack({
          title: '',
          artist: '',
          platform: 'soundcloud',
          platform_id: '',
          censorship_type: 'clean_version',
          description: '',
        });
      }
    } catch (error) {
      console.error('Error adding track:', error);
    }
  };

  // Обновление статуса трека
  const updateTrackStatus = async (trackId, status) => {
    try {
      const response = await fetch(`${API_BASE}/${trackId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      
      if (response.ok) {
        await loadTracks();
        await loadStats();
      }
    } catch (error) {
      console.error('Error updating track:', error);
    }
  };

  // Удаление трека
  const deleteTrack = async (trackId) => {
    if (!confirm('Удалить этот трек из базы?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/${trackId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadTracks();
        await loadStats();
        setSelectedTrack(null);
      }
    } catch (error) {
      console.error('Error deleting track:', error);
    }
  };

  // Поиск замены
  const findReplacement = async (track) => {
    try {
      const query = `${track.original_title || track.title} ${track.artist} explicit`;
      const response = await fetch(`/api/censorship/search-uncensored?q=${encodeURIComponent(query)}&limit=5`);
      const data = await response.json();
      
      if (data.tracks && data.tracks.length > 0) {
        const replacement = data.tracks[0];
        await fetch(`${API_BASE}/${track.id}/replacement`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            replacement_track_id: replacement.id,
            replacement_url: replacement.stream_url,
            replacement_platform: replacement.source,
          }),
        });
        await loadTracks();
        alert('Замена найдена и добавлена!');
      } else {
        alert('Замена не найдена');
      }
    } catch (error) {
      console.error('Error finding replacement:', error);
      alert('Ошибка при поиске замены');
    }
  };

  // Фильтрация по поиску
  const filteredTracks = tracks.filter(track =>
    track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    track.artist.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Форматирование даты
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  // Цвета для типов цензуры
  const censorshipTypeColors = {
    blurred: '#ff9800',
    muted: '#f44336',
    replaced: '#9c27b0',
    deleted: '#607d8b',
    clean_version: '#4caf50',
  };

  const statusColors = {
    pending: '#ff9800',
    verified: '#4caf50',
    replaced: '#2196f3',
    false_positive: '#9e9e9e',
  };

  return (
    <div className="censored-tracks-page">
      <div className="censored-tracks-header">
        <h1>🚫 База цензурированных треков</h1>
        <button 
          className="btn-add"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕' : '+ Добавить трек'}
        </button>
      </div>

      {/* Статистика */}
      {stats && (
        <div className="censored-stats">
          <div className="stat-card">
            <div className="stat-value">{stats.total_censored}</div>
            <div className="stat-label">Всего треков</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.verified_count}</div>
            <div className="stat-label">Проверено</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.replacements_found}</div>
            <div className="stat-label">Найдено замен</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.by_status?.pending || 0}</div>
            <div className="stat-label">Ожидают</div>
          </div>
        </div>
      )}

      {/* Форма добавления */}
      {showAddForm && (
        <div className="add-track-form">
          <h2>Добавить цензурированный трек</h2>
          <form onSubmit={handleAddTrack}>
            <div className="form-row">
              <input
                type="text"
                placeholder="Название трека"
                value={newTrack.title}
                onChange={(e) => setNewTrack({...newTrack, title: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Исполнитель"
                value={newTrack.artist}
                onChange={(e) => setNewTrack({...newTrack, artist: e.target.value})}
                required
              />
            </div>
            <div className="form-row">
              <input
                type="text"
                placeholder="ID на платформе"
                value={newTrack.platform_id}
                onChange={(e) => setNewTrack({...newTrack, platform_id: e.target.value})}
                required
              />
              <select
                value={newTrack.platform}
                onChange={(e) => setNewTrack({...newTrack, platform: e.target.value})}
              >
                <option value="soundcloud">SoundCloud</option>
                <option value="youtube">YouTube</option>
                <option value="vk">VK</option>
                <option value="navidrome">Navidrome</option>
              </select>
            </div>
            <div className="form-row">
              <select
                value={newTrack.censorship_type}
                onChange={(e) => setNewTrack({...newTrack, censorship_type: e.target.value})}
              >
                <option value="clean_version">Clean/Radio версия</option>
                <option value="blurred">Заблюрено (beep)</option>
                <option value="muted">Вырезано (тишина)</option>
                <option value="replaced">Заменено слово</option>
                <option value="deleted">Удалён из платформы</option>
              </select>
              <input
                type="text"
                placeholder="Описание проблемы"
                value={newTrack.description}
                onChange={(e) => setNewTrack({...newTrack, description: e.target.value})}
              />
            </div>
            <button type="submit" className="btn-submit">Добавить</button>
          </form>
        </div>
      )}

      {/* Фильтры и поиск */}
      <div className="censored-filters">
        <div className="filter-buttons">
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            Все
          </button>
          <button 
            className={filter === 'pending' ? 'active' : ''}
            onClick={() => setFilter('pending')}
          >
            Ожидают
          </button>
          <button 
            className={filter === 'verified' ? 'active' : ''}
            onClick={() => setFilter('verified')}
          >
            Проверено
          </button>
          <button 
            className={filter === 'replaced' ? 'active' : ''}
            onClick={() => setFilter('replaced')}
          >
            С заменой
          </button>
        </div>
        <input
          type="text"
          className="search-input"
          placeholder="Поиск по названию или артисту..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Список треков */}
      <div className="censored-tracks-list">
        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : filteredTracks.length === 0 ? (
          <div className="no-tracks">Треки не найдены</div>
        ) : (
          filteredTracks.map(track => (
            <div 
              key={track.id} 
              className={`censored-track-card ${selectedTrack?.id === track.id ? 'selected' : ''}`}
              onClick={() => setSelectedTrack(track)}
            >
              <div className="track-header">
                <div className="track-info">
                  <h3>{track.title}</h3>
                  <p className="artist">{track.artist}</p>
                </div>
                <div className="track-badges">
                  <span 
                    className="badge type"
                    style={{ backgroundColor: censorshipTypeColors[track.censorship_type] }}
                  >
                    {track.censorship_type}
                  </span>
                  <span 
                    className="badge status"
                    style={{ backgroundColor: statusColors[track.status] }}
                  >
                    {track.status}
                  </span>
                </div>
              </div>
              
              <div className="track-details">
                <div className="detail-row">
                  <span>Платформа:</span>
                  <strong>{track.platform}</strong>
                </div>
                {track.description && (
                  <div className="detail-row">
                    <span>Описание:</span>
                    <p>{track.description}</p>
                  </div>
                )}
                {track.censored_words && track.censored_words.length > 0 && (
                  <div className="detail-row">
                    <span>Цензурные слова:</span>
                    <code>{track.censored_words.join(', ')}</code>
                  </div>
                )}
                <div className="detail-row">
                  <span>Жалоб:</span>
                  <strong>{track.report_count || 0}</strong>
                </div>
                <div className="detail-row">
                  <span>Добавлен:</span>
                  <span>{formatDate(track.created_at)}</span>
                </div>
              </div>

              {selectedTrack?.id === track.id && (
                <div className="track-actions">
                  {track.status === 'pending' && (
                    <>
                      <button 
                        className="btn-verify"
                        onClick={() => updateTrackStatus(track.id, 'verified')}
                      >
                        ✓ Проверить
                      </button>
                      <button 
                        className="btn-false"
                        onClick={() => updateTrackStatus(track.id, 'false_positive')}
                      >
                        Ложное срабатывание
                      </button>
                    </>
                  )}
                  {!track.replacement_found && (
                    <button 
                      className="btn-find-replacement"
                      onClick={() => findReplacement(track)}
                    >
                      🔍 Найти замену
                    </button>
                  )}
                  {track.replacement_found && (
                    <div className="replacement-info">
                      <span>✅ Замена найдена</span>
                      {track.replacement_url && (
                        <a href={track.replacement_url} target="_blank" rel="noopener noreferrer">
                          Открыть
                        </a>
                      )}
                    </div>
                  )}
                  <button 
                    className="btn-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteTrack(track.id);
                    }}
                  >
                    🗑️ Удалить
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Экспорт/Импорт */}
      <div className="censored-actions">
        <button 
          className="btn-export"
          onClick={async () => {
            const response = await fetch(`${API_BASE}/export/json`);
            const data = await response.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `censored_tracks_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
          }}
        >
          📥 Экспорт в JSON
        </button>
        <label className="btn-import">
          📥 Импорт из JSON
          <input
            type="file"
            accept=".json"
            style={{ display: 'none' }}
            onChange={async (e) => {
              const file = e.target.files[0];
              if (file) {
                const reader = new FileReader();
                reader.onload = async (event) => {
                  try {
                    const data = JSON.parse(event.target.result);
                    const response = await fetch(`${API_BASE}/import/json`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify(data),
                    });
                    const result = await response.json();
                    alert(result.message);
                    loadTracks();
                    loadStats();
                  } catch (error) {
                    alert('Ошибка импорта: ' + error.message);
                  }
                };
                reader.readAsText(file);
              }
            }}
          />
        </label>
      </div>
    </div>
  );
};

export default CensoredTracks;
