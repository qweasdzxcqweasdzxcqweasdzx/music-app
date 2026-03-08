import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { musicAPI } from '../api/musicApi';
import styles from './Profile.module.css';

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    tracks: 0,
    artists: 0,
    playlists: 0,
    hours: 0,
  });
  const [loading, setLoading] = useState(true);
  const [tgUser, setTgUser] = useState(null);

  useEffect(() => {
    // Получаем данные пользователя Telegram
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      const tgUserData = tg.initDataUnsafe?.user;
      if (tgUserData) {
        setTgUser(tgUserData);
      }
    }

    // Загружаем статистику
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      // Получаем данные из API
      const userData = await musicAPI.getMe().catch(() => null);
      
      // Получаем историю
      const history = JSON.parse(localStorage.getItem('listeningHistory') || '[]');
      const liked = JSON.parse(localStorage.getItem('likedTracks') || '[]');
      const playlists = JSON.parse(localStorage.getItem('playlists') || '[]');

      // Считаем уникальных артистов
      const uniqueArtists = new Set(history.map(t => t.artist)).size;
      
      // Считаем часы прослушиваний
      const totalDuration = history.reduce((sum, t) => sum + (t.duration || 180), 0);
      const hours = Math.round(totalDuration / 3600);

      setUser(userData);
      setStats({
        tracks: history.length,
        artists: uniqueArtists,
        playlists: playlists.length,
        hours: hours,
        liked: liked.length,
      });
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('listeningHistory');
    localStorage.removeItem('likedTracks');
    localStorage.removeItem('playlists');
    
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.close();
    }
    
    navigate('/');
    window.location.reload();
  };

  const menuItems = [
    {
      icon: '🎵',
      title: 'Мои плейлисты',
      subtitle: `${stats.playlists} плейлистов`,
      action: () => navigate('/library'),
    },
    {
      icon: '❤️',
      title: 'Любимые треки',
      subtitle: `${stats.liked || 0} треков`,
      action: () => navigate('/liked'),
    },
    {
      icon: '📊',
      title: 'Статистика',
      subtitle: 'Подробная статистика',
      action: () => navigate('/stats'),
    },
    {
      icon: '🎧',
      title: 'История прослушиваний',
      subtitle: `${stats.tracks} треков`,
      action: () => navigate('/library'),
    },
    {
      icon: '⚙️',
      title: 'Настройки',
      subtitle: 'Качество, уведомления',
      action: () => navigate('/settings'),
    },
    {
      icon: '🔓',
      title: 'Источники музыки',
      subtitle: 'SoundCloud, VK, YouTube',
      action: () => navigate('/sources'),
    },
  ];

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Загрузка профиля...</p>
      </div>
    );
  }

  return (
    <div className={styles.profile}>
      {/* Header с аватаром */}
      <div className={styles.header}>
        <div className={styles.avatar}>
          {tgUser?.photo_url ? (
            <img src={tgUser.photo_url} alt={tgUser.first_name} />
          ) : (
            <span className={styles.avatarPlaceholder}>
              {tgUser?.first_name?.[0] || 'U'}
            </span>
          )}
        </div>
        <div className={styles.userInfo}>
          <h1 className={styles.userName}>
            {tgUser?.first_name || 'Пользователь'}
            {tgUser?.last_name && ` ${tgUser.last_name}`}
          </h1>
          <p className={styles.userUsername}>
            @{tgUser?.username || 'telegram_user'}
          </p>
          {user?.is_premium && (
            <span className={styles.premiumBadge}>Premium</span>
          )}
        </div>
      </div>

      {/* Статистика */}
      <div className={styles.stats}>
        <div className={styles.statItem}>
          <span className={styles.statValue}>{stats.tracks}</span>
          <span className={styles.statLabel}>Треков</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statValue}>{stats.artists}</span>
          <span className={styles.statLabel}>Артистов</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statValue}>{stats.hours}</span>
          <span className={styles.statLabel}>Часов</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statValue}>{stats.liked || 0}</span>
          <span className={styles.statLabel}>Лайков</span>
        </div>
      </div>

      {/* Меню профиля */}
      <div className={styles.menu}>
        {menuItems.map((item, index) => (
          <div
            key={index}
            className={styles.menuItem}
            onClick={item.action}
          >
            <span className={styles.menuIcon}>{item.icon}</span>
            <div className={styles.menuInfo}>
              <span className={styles.menuTitle}>{item.title}</span>
              <span className={styles.menuSubtitle}>{item.subtitle}</span>
            </div>
            <svg className={styles.menuArrow} viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </div>
        ))}
      </div>

      {/* Кнопка выхода */}
      <button className={styles.logoutBtn} onClick={handleLogout}>
        Выйти из аккаунта
      </button>

      {/* Версия приложения */}
      <div className={styles.version}>
        Ultimate Music App v3.0
      </div>
    </div>
  );
};

export default Profile;
