import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './TabBar.module.css';

const TabBar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const tabs = [
    { path: '/', icon: 'home', label: 'Главная' },
    { path: '/search', icon: 'search', label: 'Поиск' },
    { path: '/library', icon: 'library', label: 'Медиатека' },
    { path: '/mixer', icon: 'mix', label: 'Миксер' },
  ];

  const getIcon = (iconName) => {
    switch (iconName) {
      case 'home':
        return (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M12.5 2.04L2 10.5h3v9h6v-6h2v6h6v-9h3L12.5 2.04M12 3.53L19 9.17V18h-3v-6H8v6H5V9.17l7-5.64z"/>
          </svg>
        );
      case 'search':
        return (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M10.53 2a8.53 8.53 0 0 1 6.97 13.47l5.3 5.3-1.42 1.42-5.3-5.3A8.53 8.53 0 1 1 10.53 2m0 2a6.53 6.53 0 1 0 0 13.06 6.53 6.53 0 0 0 0-13.06z"/>
          </svg>
        );
      case 'library':
        return (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M4 6h2v12H4V6m4 0h2v12H8V6m4 0h8v12h-8V6"/>
          </svg>
        );
      case 'mix':
        return (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <nav className="tab-bar">
      {tabs.map((tab) => (
        <Link
          key={tab.path}
          to={tab.path}
          className={`tab-item ${isActive(tab.path) ? 'active' : ''}`}
        >
          <div className="tab-icon">
            {getIcon(tab.icon)}
          </div>
          <span className="tab-label">{tab.label}</span>
        </Link>
      ))}
    </nav>
  );
};

export default TabBar;
