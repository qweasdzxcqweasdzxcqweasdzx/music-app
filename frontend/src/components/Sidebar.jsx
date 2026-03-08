import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const mainNavItems = [
  { icon: 'home', label: 'Главная', path: '/' },
  { icon: 'search', label: 'Поиск', path: '/search' },
  { icon: 'library', label: 'Медиатека', path: '/library' },
];

const musicNavItems = [
  { icon: 'mix', label: 'Smart Mixer', path: '/mixer', color: '#e74c3c' },
  { icon: 'ai', label: 'AI Студия', path: '/ai-studio', color: '#9b59b6' },
  { icon: 'daily', label: 'Daily Mixes', path: '/daily-mixes', color: '#1db954' },
];

const libraryNavItems = [
  { icon: 'heart', label: 'Любимые треки', path: '/liked' },
  { icon: 'queue', label: 'Очередь', path: '/queue' },
];

const settingsNavItems = [
  { icon: 'sources', label: 'Источники', path: '/sources' },
  { icon: 'stats', label: 'Статистика', path: '/stats' },
  { icon: 'equalizer', label: 'Эквалайзер', path: '/equalizer' },
];

export default function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation();
  const [likedCount, setLikedCount] = useState(0);
  const [queueCount, setQueueCount] = useState(0);

  useEffect(() => {
    const liked = localStorage.getItem('likedTracks');
    if (liked) {
      setLikedCount(JSON.parse(liked).length);
    }
    
    const queue = localStorage.getItem('queue');
    if (queue) {
      setQueueCount(JSON.parse(queue).length);
    }
  }, []);

  const renderIcon = (iconName) => {
    const icons = {
      home: (
        <path fill="currentColor" d="M12.5 2.04L2 10.5h3v9h6v-6h2v6h6v-9h3L12.5 2.04M12 3.53L19 9.17V18h-3v-6H8v6H5V9.17l7-5.64z"/>
      ),
      search: (
        <path fill="currentColor" d="M10.53 2a8.53 8.53 0 0 1 6.97 13.47l5.3 5.3-1.42 1.42-5.3-5.3A8.53 8.53 0 1 1 10.53 2m0 2a6.53 6.53 0 1 0 0 13.06 6.53 6.53 0 0 0 0-13.06z"/>
      ),
      library: (
        <path fill="currentColor" d="M4 6h2v12H4V6m4 0h2v12H8V6m4 0h8v12h-8V6"/>
      ),
      mix: (
        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      ),
      ai: (
        <path fill="currentColor" d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5 2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5 2.5 2.5 0 0 0 2.5 2.5 2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5z"/>
      ),
      daily: (
        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15H9v-2h2v2zm0-4H9V7h2v6zm4 4h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      ),
      heart: (
        <path fill="#1db954" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      ),
      queue: (
        <path fill="currentColor" d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
      ),
      sources: (
        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
      ),
      stats: (
        <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2M9 17H7v-7h2v7m4 0h-2V7h2v10m4 0h-2v-4h2v4z"/>
      ),
      equalizer: (
        <path fill="currentColor" d="M10 20h4V4h-4v16zm-6 0h4v-8H4v8zM16 9v11h4V9h-4z"/>
      ),
      plus: (
        <path fill="currentColor" d="M15.25 8a.75.75 0 0 1-.75.75H8.75v5.75a.75.75 0 0 1-1.5 0V8.75H1.5a.75.75 0 0 1 0-1.5h5.75V1.5a.75.75 0 0 1 1.5 0v5.75h5.75a.75.75 0 0 1 .75.75z"/>
      ),
    };
    
    return (
      <svg viewBox="0 0 24 24" width="24" height="24">
        {icons[iconName] || icons.home}
      </svg>
    );
  };

  const NavItem = ({ item, active }) => (
    <Link
      to={item.path}
      className={`nav-item ${active ? 'active' : ''}`}
      style={{ '--item-color': item.color || 'currentColor' }}
    >
      <span className="nav-icon" style={{ color: item.color }}>
        {renderIcon(item.icon)}
      </span>
      {!collapsed && <span className="nav-label">{item.label}</span>}
      {!collapsed && item.badge && (
        <span className="nav-badge">{item.badge}</span>
      )}
    </Link>
  );

  const NavSection = ({ title, items }) => (
    <div className="sidebar-section">
      {!collapsed && title && <h3 className="section-title">{title}</h3>}
      <ul className="nav-list">
        {items.map((item) => (
          <li key={item.path}>
            <NavItem item={item} active={location.pathname === item.path} />
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button
          className="collapse-btn"
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? 'Развернуть' : 'Свернуть'}
        >
          <svg viewBox="0 0 16 16" width="16" height="16">
            {collapsed ? (
              <path fill="currentColor" d="M10.56 1.76a.75.75 0 0 1 1.06 0l3.75 3.75a.75.75 0 0 1 0 1.06l-3.75 3.75a.75.75 0 1 1-1.06-1.06l2.22-2.22H.75a.75.75 0 0 1 0-1.5h12.03L10.56 3.28a.75.75 0 0 1 0-1.06Z"/>
            ) : (
              <path fill="currentColor" d="M5.44 1.76a.75.75 0 0 0-1.06 0L.63 5.51a.75.75 0 0 0 0 1.06l3.75 3.75a.75.75 0 1 0 1.06-1.06L3.22 7.03h12.03a.75.75 0 0 0 0-1.5H3.22l2.22-2.21a.75.75 0 0 0 0-1.06Z"/>
            )}
          </svg>
        </button>
        {!collapsed && (
          <Link to="/" className="logo">
            <span className="logo-text">🎵 Ultimate Music</span>
          </Link>
        )}
      </div>

      <nav className="sidebar-nav">
        <NavSection items={mainNavItems} />
        <NavSection title="Музыка" items={musicNavItems} />
        <NavSection title="Библиотека" items={libraryNavItems.map(item => ({
          ...item,
          badge: item.path === '/liked' ? likedCount : item.path === '/queue' ? queueCount : null
        }))} />
        <NavSection title="Настройки" items={settingsNavItems} />
      </nav>

      <div className="sidebar-footer">
        {!collapsed && (
          <div className="version">
            v3.0 Ultimate
          </div>
        )}
      </div>
    </aside>
  );
}
