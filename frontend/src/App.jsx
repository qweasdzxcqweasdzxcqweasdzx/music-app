import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { PlayerProvider } from './contexts/PlayerContext';
import Player from './components/Player';
import TabBar from './components/TabBar';
import Home from './pages/Home';
import Search from './pages/Search';
import Library from './pages/Library';
import PlaylistDetail from './pages/PlaylistDetail';
import Queue from './components/Queue';
import Artist from './pages/Artist';
import Album from './pages/Album';
import DailyMixes from './pages/DailyMixes';
import FullPlayer from './pages/FullPlayer';
import Stats from './pages/Stats';
import AIStudio from './pages/AIStudio';
import SmartMixer from './pages/SmartMixer';
import Sources from './pages/Sources';
import GenreDetail from './pages/GenreDetail';
import CensoredTracks from './pages/CensoredTracks';

import './index.css';

function App() {
  const [tgUser, setTgUser] = useState(null);

  // Инициализация Telegram
  useEffect(() => {
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      
      // Настраиваем цвета
      tg.setHeaderColor('#121212');
      tg.setBackgroundColor('#121212');
      
      setTgUser(tg.initDataUnsafe?.user);
      
      // Настраиваем MainButton
      tg.MainButton.setParams({
        color: '#ff5500',
        text_color: '#ffffff'
      });
    }
  }, []);

  // Обработчик аутентификации
  useEffect(() => {
    const handleAuthRequired = () => {
      console.log('Authentication required');
    };

    window.addEventListener('auth-required', handleAuthRequired);
    return () => window.removeEventListener('auth-required', handleAuthRequired);
  }, []);

  return (
    <PlayerProvider>
      <Router basename="/">
        <div className="app">
          <main className="main-content">
            <Routes>
              {/* Основные страницы */}
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<Search />} />
              <Route path="/library" element={<Library />} />
              <Route path="/liked" element={<PlaylistDetail playlistType="liked" />} />
              <Route path="/playlist/:id" element={<PlaylistDetail />} />
              <Route path="/queue" element={<Queue />} />

              {/* Музыка */}
              <Route path="/artist/:id" element={<Artist />} />
              <Route path="/album/:id" element={<Album />} />

              {/* Персональное */}
              <Route path="/daily-mixes" element={<DailyMixes />} />
              <Route path="/stats" element={<Stats />} />

              {/* Smart Mixer */}
              <Route path="/mixer" element={<SmartMixer />} />
              <Route path="/mixer/radio/:trackId" element={<SmartMixer />} />

              {/* AI Studio */}
              <Route path="/ai-studio" element={<AIStudio />} />

              {/* Источники */}
              <Route path="/sources" element={<Sources />} />

              {/* Цензурированные треки */}
              <Route path="/censored" element={<CensoredTracks />} />

              {/* Жанры */}
              <Route path="/genre/:genreId" element={<GenreDetail />} />

              {/* Полный плеер */}
              <Route path="/player" element={<FullPlayer />} />
            </Routes>
          </main>
          
          {/* Плеер всегда виден */}
          <Player />
          
          {/* Нижняя навигация */}
          <TabBar />
        </div>
      </Router>
    </PlayerProvider>
  );
}

export default App;
