/**
 * API Client для Ultimate Music App
 * SoundCloud API + Telegram Mini Apps
 */

// HTTPS URL через Cloudflare Tunnel + CORS Proxy (порт 8081)
const API_URL = 'https://mariah-iowa-predict-intake.trycloudflare.com/api';

class MusicAPI {
  constructor() {
    this.token = localStorage.getItem('token');
    this.ws = null;
    this.wsListeners = new Map();
    this.initTelegramAuth();
  }

  // ==================== AUDIO STREAMING ====================
  
  /**
   * Получить URL для воспроизведения трека
   */
  async getAudioStreamUrl(videoId) {
    // Используем прокси для обхода CORS
    return `${API_URL.replace('/api', '')}/audio/proxy/${videoId}`;
  }

  /**
   * Воспроизвести трек
   */
  async playTrack(videoId, title, artist) {
    const streamUrl = await this.getAudioStreamUrl(videoId);
    return {
      url: streamUrl,
      title: title,
      artist: artist,
      videoId: videoId
    };
  }

  // Инициализация аутентификации Telegram
  async initTelegramAuth() {
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      
      // Получаем initData для аутентификации
      const initData = tg.initData;
      if (initData && !this.token) {
        try {
          await this.authTelegram(initData);
        } catch (error) {
          console.error('Telegram auth failed:', error);
        }
      }
    }
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  getToken() {
    return this.token;
  }

  removeToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        this.removeToken();
        window.dispatchEvent(new CustomEvent('auth-required'));
        throw new Error('Unauthorized');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // ==================== Аутентификация ====================

  async authTelegram(initData) {
    const response = await fetch(`${API_URL}/auth/telegram`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `init_data=${encodeURIComponent(initData)}`,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Auth failed' }));
      throw new Error(error.detail || 'Authentication failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async getMe() {
    return this.request('/me');
  }

  // ==================== Источники ====================

  async getSources() {
    return this.request('/sources');
  }

  // ==================== Поиск ====================

  async search(query, limit = 20, type = 'all') {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      type,
    });
    return this.request(`/search?${params}`);
  }

  async unifiedSearch(query, limit = 20, sources = null) {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    if (sources) {
      params.set('sources', sources.join(','));
    }
    return this.request(`/search/unified?${params}`);
  }

  // ==================== Треки ====================

  async getTrack(trackId) {
    return this.request(`/tracks/${trackId}`);
  }

  async getTrackStream(trackId) {
    return this.request(`/tracks/${trackId}/stream`);
  }

  async getTrackLyrics(trackId, trackTitle, artistName) {
    const params = new URLSearchParams();
    if (trackTitle) params.set('track_title', trackTitle);
    if (artistName) params.set('artist_name', artistName);
    return this.request(`/tracks/${trackId}/lyrics?${params}`);
  }

  // ==================== Артисты ====================

  async getArtist(artistId) {
    return this.request(`/artists/${artistId}`);
  }

  async getArtistTopTracks(artistId, limit = 10) {
    return this.request(`/artists/${artistId}/tracks?limit=${limit}`);
  }

  async getArtistAlbums(artistId, includeGroups = 'album,single', limit = 20) {
    return this.request(`/artists/${artistId}/albums?include_groups=${includeGroups}&limit=${limit}`);
  }

  async getArtistRecommendations(artistId, limit = 20) {
    return this.request(`/artists/${artistId}/recommendations?limit=${limit}`);
  }

  // ==================== Альбомы ====================

  async getAlbum(albumId) {
    return this.request(`/albums/${albumId}`);
  }

  async getAlbumTracks(albumId, limit = 50) {
    return this.request(`/albums/${albumId}/tracks?limit=${limit}`);
  }

  async getSingle(singleId) {
    return this.request(`/singles/${singleId}`);
  }

  // ==================== Рекомендации ====================

  async getRecommendations(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.seedArtists) queryParams.set('seed_artists', params.seedArtists);
    if (params.seedTracks) queryParams.set('seed_tracks', params.seedTracks);
    if (params.seedGenres) queryParams.set('seed_genres', params.seedGenres);
    if (params.limit) queryParams.set('limit', params.limit);

    return this.request(`/recommendations?${queryParams}`);
  }

  async getForYouRecommendations(limit = 20) {
    return this.request(`/recommendations/for-you?limit=${limit}`);
  }

  async getMoodRecommendations(mood, limit = 20) {
    return this.request(`/recommendations/mood/${mood}?limit=${limit}`);
  }

  // ==================== Жанры ====================

  async getGenres() {
    return this.request('/genres');
  }

  async getGenreTracks(genreId, limit = 20) {
    return this.request(`/genres/${genreId}?limit=${limit}`);
  }

  // ==================== Чарты ====================

  async getTopTracks(limit = 20) {
    return this.request(`/top?limit=${limit}`);
  }

  async getNewReleases(limit = 20) {
    return this.request(`/new?limit=${limit}`);
  }

  async getFeaturedPlaylists(limit = 10) {
    return this.request(`/featured?limit=${limit}`);
  }

  // ==================== SoundCloud ====================

  async getTrending(limit = 20, genre = null) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (genre) params.set('genre', genre);
    return this.request(`/soundcloud/trending?${params}`);
  }

  async getUserTracks(userId, limit = 20) {
    return this.request(`/artists/${userId}/tracks?limit=${limit}`);
  }

  async getUserPlaylists(userId, limit = 20) {
    return this.request(`/artists/${userId}/albums?limit=${limit}`);
  }

  // ==================== Smart Mixer ====================

  async getSmartMix(limit = 50, sources = null) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (sources) params.set('sources', sources.join(','));
    return this.request(`/mixer/smart?${params}`);
  }

  async getInfiniteRadio(trackId, limit = 50, source = 'soundcloud') {
    return this.request(`/mixer/radio/${trackId}?limit=${limit}&source=${source}`);
  }

  async getMoodMix(mood, limit = 30) {
    return this.request(`/mixer/mood/${mood}?limit=${limit}`);
  }

  async getGenreMix(genre, limit = 40, sources = null) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (sources) params.set('sources', sources.join(','));
    return this.request(`/mixer/genre/${genre}?${params}`);
  }

  // ==================== AI Генерация ====================

  async generateMusic(provider, prompt, options = {}) {
    return this.request('/ai/generate', {
      method: 'POST',
      body: JSON.stringify({
        provider,
        prompt,
        ...options,
      }),
    });
  }

  async getGenerationStatus(taskId, provider) {
    return this.request(`/ai/status/${taskId}?provider=${provider}`);
  }

  async separateStems(audioUrl, stemType = 'vocals', provider = 'lalal') {
    return this.request(`/ai/separate?stem_type=${stemType}&provider=${provider}`, {
      method: 'POST',
      body: JSON.stringify({ audio_url: audioUrl }),
    });
  }

  async generateVoice(text, voiceId = '21m00Tcm4TlvDq8ikWAM', provider = 'elevenlabs') {
    return this.request('/ai/voice', {
      method: 'POST',
      body: JSON.stringify({ text, voice_id: voiceId, provider }),
    });
  }

  async getAvailableVoices(provider = 'elevenlabs') {
    return this.request(`/ai/voices?provider=${provider}`);
  }

  // ==================== Плейлисты ====================

  async createPlaylist(name, description = '', isPublic = false) {
    return this.request('/playlists', {
      method: 'POST',
      body: JSON.stringify({ name, description, is_public: isPublic }),
    });
  }

  async getPlaylists() {
    return this.request('/playlists');
  }

  async getPlaylist(playlistId) {
    return this.request(`/playlists/${playlistId}`);
  }

  async updatePlaylist(playlistId, updates) {
    return this.request(`/playlists/${playlistId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deletePlaylist(playlistId) {
    return this.request(`/playlists/${playlistId}`, {
      method: 'DELETE',
    });
  }

  async addTrackToPlaylist(playlistId, trackId) {
    return this.request(`/playlists/${playlistId}/tracks?track_id=${trackId}`, {
      method: 'POST',
    });
  }

  async removeTrackFromPlaylist(playlistId, trackId) {
    return this.request(`/playlists/${playlistId}/tracks/${trackId}`, {
      method: 'DELETE',
    });
  }

  // ==================== История и лайки ====================

  async getHistory(limit = 50) {
    return this.request(`/history?limit=${limit}`);
  }

  async addToHistory(trackId, playDuration = 0) {
    return this.request(`/history?track_id=${trackId}&play_duration=${playDuration}`, {
      method: 'POST',
    });
  }

  async getLikes() {
    return this.request('/likes');
  }

  async addLike(trackId) {
    return this.request(`/likes/${trackId}`, {
      method: 'POST',
    });
  }

  async removeLike(trackId) {
    return this.request(`/likes/${trackId}`, {
      method: 'DELETE',
    });
  }

  // ==================== Daily Mixes ====================

  async getDailyMixes() {
    return this.request('/daily-mixes');
  }

  async getReleaseRadar() {
    return this.request('/release-radar');
  }

  async getDiscoverWeekly() {
    return this.request('/discover-weekly');
  }

  // ==================== Статистика ====================

  async getStats() {
    return this.request('/stats');
  }

  // ==================== Очередь ====================

  async getQueue() {
    return this.request('/queue');
  }

  async addToQueue(trackId) {
    return this.request('/queue', {
      method: 'POST',
      body: JSON.stringify({ track_id: trackId }),
    });
  }

  async clearQueue() {
    return this.request('/queue/clear', {
      method: 'POST',
    });
  }

  // ==================== WebSocket ====================

  connectWebSocket() {
    if (this.ws?.readyState === WebSocket.OPEN) return this.ws;

    const wsUrl = `ws://${window.location.hostname}:8000/ws`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      // Аутентификация
      if (this.token) {
        this.ws.send(JSON.stringify({
          type: 'auth',
          payload: { token: this.token },
        }));
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Переподключение через 5 секунд
      setTimeout(() => this.connectWebSocket(), 5000);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const listeners = this.wsListeners.get(data.type) || [];
      listeners.forEach(callback => callback(data));
    };

    return this.ws;
  }

  addWebSocketListener(eventType, callback) {
    if (!this.wsListeners.has(eventType)) {
      this.wsListeners.set(eventType, []);
    }
    this.wsListeners.get(eventType).push(callback);

    return () => {
      const listeners = this.wsListeners.get(eventType);
      const index = listeners.indexOf(callback);
      if (index !== -1) listeners.splice(index, 1);
    };
  }

  sendWebSocket(type, payload = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    }
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.wsListeners.clear();
  }

  // ==================== Jam Session ====================

  async createJam() {
    return this.request('/jam', { method: 'POST' });
  }

  async getJamSession(sessionId) {
    return this.request(`/jam/${sessionId}`);
  }

  async joinJamSession(sessionId) {
    return this.request(`/jam/${sessionId}/join`, { method: 'POST' });
  }

  async leaveJamSession(sessionId) {
    return this.request(`/jam/${sessionId}/leave`, { method: 'POST' });
  }

  // ==================== Задачи (Celery) ====================

  async generateMixTask(limit = 50) {
    return this.request('/tasks/generate-mix', {
      method: 'POST',
      body: JSON.stringify({ limit }),
    });
  }

  async getTaskStatus(taskId) {
    return this.request(`/tasks/status/${taskId}`);
  }
}

// Экспорт глобального экземпляра
export const musicAPI = new MusicAPI();
export default musicAPI;
