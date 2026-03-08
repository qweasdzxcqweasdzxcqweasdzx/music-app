/**
 * PlayerContext - Управление состоянием плеера
 * Централизованное управление воспроизведением, очередью и настройками
 */

import { createContext, useState, useEffect, useRef, useCallback, useContext } from 'react';
import { musicAPI } from '../api/musicApi';

export const PlayerContext = createContext(null);

// Хук для удобного использования контекста
export function usePlayer() {
  const context = useContext(PlayerContext);
  if (!context) {
    throw new Error('usePlayer must be used within PlayerProvider');
  }
  return context;
}

export function PlayerProvider({ children }) {
  // Состояние трека
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  
  // Громкость и настройки
  const [volume, setVolumeState] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const [shuffle, setShuffle] = useState(false);
  const [repeat, setRepeat] = useState('off'); // 'off', 'all', 'one'
  
  // Очередь
  const [queue, setQueue] = useState([]);
  const [queueIndex, setQueueIndex] = useState(-1);
  
  // Аудио элемент
  const [audioElement, setAudioElement] = useState(null);
  
  // Дополнительно
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lyrics, setLyrics] = useState(null);
  
  const fadeTimeoutRef = useRef(null);

  // Инициализация
  useEffect(() => {
    // Восстановление из localStorage
    const savedVolume = localStorage.getItem('volume');
    if (savedVolume) setVolumeState(parseFloat(savedVolume));
    
    const savedShuffle = localStorage.getItem('shuffle');
    if (savedShuffle) setShuffle(JSON.parse(savedShuffle));
    
    const savedRepeat = localStorage.getItem('repeat');
    if (savedRepeat) setRepeat(savedRepeat);

    // Создаем аудио элемент
    const audio = new Audio();
    audio.crossOrigin = 'anonymous';
    audio.preload = 'metadata';
    setAudioElement(audio);

    return () => {
      if (fadeTimeoutRef.current) clearTimeout(fadeTimeoutRef.current);
      audio.pause();
      audio.src = '';
    };
  }, []);

  // Обработчики аудио элемента
  useEffect(() => {
    if (!audioElement) return;

    const handleTimeUpdate = () => setProgress(audioElement.currentTime);
    const handleLoadedMetadata = () => setDuration(audioElement.duration);
    const handleEnded = handleTrackEnd;
    const handleError = (e) => {
      console.error('Audio error:', e);
      setError('Ошибка воспроизведения');
      setIsLoading(false);
    };

    audioElement.addEventListener('timeupdate', handleTimeUpdate);
    audioElement.addEventListener('loadedmetadata', handleLoadedMetadata);
    audioElement.addEventListener('ended', handleEnded);
    audioElement.addEventListener('error', handleError);

    return () => {
      audioElement.removeEventListener('timeupdate', handleTimeUpdate);
      audioElement.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audioElement.removeEventListener('ended', handleEnded);
      audioElement.removeEventListener('error', handleError);
    };
  }, [audioElement, queue, queueIndex, shuffle, repeat]);

  // Сохранение настроек
  useEffect(() => {
    localStorage.setItem('volume', volume.toString());
    if (audioElement) audioElement.volume = isMuted ? 0 : volume;
  }, [volume, isMuted, audioElement]);

  useEffect(() => {
    localStorage.setItem('shuffle', JSON.stringify(shuffle));
  }, [shuffle]);

  useEffect(() => {
    localStorage.setItem('repeat', repeat);
  }, [repeat]);

  const handleTrackEnd = useCallback(() => {
    if (repeat === 'one') {
      audioElement.currentTime = 0;
      audioElement.play();
    } else {
      nextTrack();
    }
  }, [repeat, queue, queueIndex, shuffle]);

  // Получение URL трека
  const getTrackUrl = async (track) => {
    if (track.stream_url) return track.stream_url;
    if (track.preview_url) return track.preview_url;
    
    try {
      const data = await musicAPI.getTrackStream(track.id);
      return data.stream_url;
    } catch {
      return null;
    }
  };

  // Воспроизведение трека
  const playTrack = useCallback(async (track, newQueue = [], startIndex = 0) => {
    if (!audioElement) return;
    
    setIsLoading(true);
    setError(null);

    try {
      // Обновление очереди
      if (newQueue.length > 0) {
        setQueue(newQueue);
        setQueueIndex(startIndex);
      } else if (!queue.length) {
        setQueue([track]);
        setQueueIndex(0);
      }

      setCurrentTrack(track);
      
      // Получение URL
      const url = await getTrackUrl(track);
      if (!url) throw new Error('No stream URL');

      // Плавное затухание
      if (isPlaying) {
        await fadeOut(audioElement, 200);
      }

      audioElement.src = url;
      audioElement.volume = isMuted ? 0 : volume;
      
      await audioElement.play();
      setIsPlaying(true);
      setIsLoading(false);

      // Сохранение в историю
      addToHistory(track);

      // Загрузка текста
      if (track.id) {
        loadLyrics(track.id);
      }
    } catch (err) {
      console.error('Playback error:', err);
      setError(err.message);
      setIsLoading(false);
      nextTrack();
    }
  }, [audioElement, queue, isPlaying, volume, isMuted]);

  // Переключение play/pause
  const togglePlay = useCallback(() => {
    if (!audioElement || !currentTrack) return;

    if (isPlaying) {
      audioElement.pause();
      setIsPlaying(false);
    } else {
      audioElement.play().catch(console.error);
      setIsPlaying(true);
    }
  }, [audioElement, currentTrack, isPlaying]);

  // Следующий трек
  const nextTrack = useCallback(() => {
    if (!queue.length) return;

    let nextIndex;
    if (shuffle) {
      nextIndex = Math.floor(Math.random() * queue.length);
    } else {
      nextIndex = (queueIndex + 1) % queue.length;
    }

    if (nextIndex !== queueIndex) {
      playTrack(queue[nextIndex], queue, nextIndex);
    } else if (repeat === 'off') {
      setIsPlaying(false);
      setProgress(0);
    }
  }, [queue, queueIndex, shuffle, repeat, playTrack]);

  // Предыдущий трек
  const prevTrack = useCallback(() => {
    if (!queue.length) return;

    // Если прошло больше 3 секунд, начинаем трек заново
    if (progress > 3) {
      audioElement.currentTime = 0;
      return;
    }

    const prevIndex = queueIndex === 0 ? queue.length - 1 : queueIndex - 1;
    playTrack(queue[prevIndex], queue, prevIndex);
  }, [queue, queueIndex, progress, audioElement, playTrack]);

  // Перемотка
  const seek = useCallback((time) => {
    if (audioElement) {
      audioElement.currentTime = Math.max(0, Math.min(time, duration));
      setProgress(audioElement.currentTime);
    }
  }, [audioElement, duration]);

  // Громкость
  const setVolume = useCallback((newVolume) => {
    setVolumeState(Math.max(0, Math.min(1, newVolume)));
    setIsMuted(newVolume === 0);
  }, []);

  const toggleMute = useCallback(() => {
    setIsMuted(!isMuted);
  }, [isMuted]);

  // Очередь
  const addToQueue = useCallback((track) => {
    setQueue(prev => [...prev, track]);
  }, []);

  const removeFromQueue = useCallback((index) => {
    setQueue(prev => prev.filter((_, i) => i !== index));
    if (index < queueIndex) {
      setQueueIndex(prev => prev - 1);
    }
  }, [queueIndex]);

  const clearQueue = useCallback(() => {
    setQueue([]);
    setQueueIndex(-1);
  }, []);

  const playQueue = useCallback((index) => {
    if (index >= 0 && index < queue.length) {
      playTrack(queue[index], queue, index);
    }
  }, [queue, playTrack]);

  // Настройки
  const toggleShuffle = useCallback(() => {
    setShuffle(prev => !prev);
  }, []);

  const toggleRepeat = useCallback(() => {
    setRepeat(prev => {
      if (prev === 'off') return 'all';
      if (prev === 'all') return 'one';
      return 'off';
    });
  }, []);

  // Утилиты
  const fadeOut = (audio, duration = 200) => {
    return new Promise((resolve) => {
      const steps = 10;
      const stepDuration = duration / steps;
      const stepVolume = volume / steps;
      let currentStep = 0;

      const fade = () => {
        currentStep++;
        audio.volume = Math.max(0, volume - (stepVolume * currentStep));
        
        if (currentStep < steps) {
          fadeTimeoutRef.current = setTimeout(fade, stepDuration);
        } else {
          resolve();
        }
      };

      fade();
    });
  };

  const fadeIn = (audio, duration = 200) => {
    return new Promise((resolve) => {
      const steps = 10;
      const stepDuration = duration / steps;
      const stepVolume = volume / steps;
      let currentStep = 0;

      const fade = () => {
        currentStep++;
        audio.volume = Math.min(volume, stepVolume * currentStep);
        
        if (currentStep < steps) {
          fadeTimeoutRef.current = setTimeout(fade, stepDuration);
        } else {
          resolve();
        }
      };

      fade();
    });
  };

  const addToHistory = (track) => {
    const history = JSON.parse(localStorage.getItem('listeningHistory') || '[]');
    const existingIndex = history.findIndex(t => t.id === track.id);
    
    if (existingIndex !== -1) {
      history.splice(existingIndex, 1);
    }
    
    history.unshift({ ...track, playedAt: new Date().toISOString() });
    localStorage.setItem('listeningHistory', JSON.stringify(history.slice(-100)));
  };

  const loadLyrics = async (trackId) => {
    try {
      const data = await musicAPI.getLyrics(trackId);
      setLyrics(data);
    } catch {
      setLyrics(null);
    }
  };

  const clearLyrics = () => setLyrics(null);

  // Форматирование времени
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const value = {
    // Состояние
    currentTrack,
    isPlaying,
    isLoading,
    progress,
    duration,
    volume,
    isMuted,
    shuffle,
    repeat,
    queue,
    queueIndex,
    error,
    lyrics,
    audioElement,
    
    // Управление
    playTrack,
    togglePlay,
    nextTrack,
    prevTrack,
    seek,
    setVolume,
    toggleMute,
    toggleShuffle,
    toggleRepeat,
    
    // Очередь
    addToQueue,
    removeFromQueue,
    clearQueue,
    playQueue,
    
    // Утилиты
    formatTime,
    clearLyrics,
    setError,
  };

  return (
    <PlayerContext.Provider value={value}>
      {children}
    </PlayerContext.Provider>
  );
}
