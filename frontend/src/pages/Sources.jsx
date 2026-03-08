import React, { useState, useEffect } from 'react';
import { musicAPI } from '../api/musicApi';
import styles from './Sources.module.css';

const SOURCE_CONFIG = {
  spotify: {
    name: 'Spotify',
    description: 'Официальный API с миллионами треков',
    color: '#1DB954',
    icon: '🎵',
    setupUrl: 'https://developer.spotify.com/dashboard',
  },
  soundcloud: {
    name: 'SoundCloud',
    description: 'Независимые артисты и ремиксы',
    color: '#ff5500',
    icon: '🔊',
    setupUrl: 'https://soundcloud.com/you/apps',
  },
  navidrome: {
    name: 'Navidrome',
    description: 'Ваша личная коллекция (Subsonic API)',
    color: '#3498db',
    icon: '🏠',
    setupUrl: 'https://www.navidrome.org/',
  },
  vk: {
    name: 'VK Music',
    description: 'Резервный источник',
    color: '#0077FF',
    icon: '🎶',
    setupUrl: 'https://dev.vk.com/',
  },
  youtube: {
    name: 'YouTube',
    description: 'Поиск оригиналов и видео',
    color: '#FF0000',
    icon: '📺',
    setupUrl: 'https://console.cloud.google.com/apis',
  },
  ai: {
    name: 'AI Сервисы',
    description: 'Suno, Mubert, LALAL.AI, ElevenLabs',
    color: '#9b59b6',
    icon: '🤖',
    setupUrl: '#',
  },
};

export default function Sources() {
  const [sources, setSources] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [showConfig, setShowConfig] = useState(null);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      const data = await musicAPI.getSources();
      setSources(data.sources || {});
    } catch (error) {
      console.error('Error loading sources:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const isConnected = (sourceId) => {
    return sources[sourceId]?.available || false;
  };

  return (
    <div className={styles.sources}>
      <header className={styles.header}>
        <h1>🔌 Источники музыки</h1>
        <p>Подключите музыкальные сервисы для доступа к вашей библиотеке</p>
      </header>

      {isLoading ? (
        <div className={styles.loading}>Загрузка...</div>
      ) : (
        <div className={styles.grid}>
          {Object.entries(SOURCE_CONFIG).map(([id, config]) => {
            const connected = isConnected(id);
            
            return (
              <div 
                key={id}
                className={`${styles.card} ${connected ? styles.connected : ''}`}
                style={{ '--source-color': config.color }}
              >
                <div className={styles.cardHeader}>
                  <span className={styles.icon}>{config.icon}</span>
                  <div className={styles.status}>
                    {connected ? (
                      <span className={styles.connectedBadge}>
                        ✅ Подключено
                      </span>
                    ) : (
                      <span className={styles.disconnectedBadge}>
                        ❌ Не подключено
                      </span>
                    )}
                  </div>
                </div>

                <h3 className={styles.name}>{config.name}</h3>
                <p className={styles.description}>{config.description}</p>

                <div className={styles.actions}>
                  {connected ? (
                    <>
                      <button className={styles.settingsButton}>
                        ⚙️ Настройки
                      </button>
                      <button className={styles.disconnectButton}>
                        Отключить
                      </button>
                    </>
                  ) : (
                    <button 
                      className={styles.connectButton}
                      onClick={() => setShowConfig(id)}
                    >
                      🔗 Подключить
                    </button>
                  )}
                </div>

                <a 
                  href={config.setupUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.setupLink}
                >
                  📚 Как настроить →
                </a>
              </div>
            );
          })}
        </div>
      )}

      {/* Модальное окно настройки */}
      {showConfig && (
        <div className={styles.modal} onClick={() => setShowConfig(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <h2>Настройка {SOURCE_CONFIG[showConfig].name}</h2>
            
            <div className={styles.modalBody}>
              <p>
                Для подключения {SOURCE_CONFIG[showConfig].name} вам нужно:
              </p>
              
              <ol className={styles.steps}>
                <li>Перейдите на страницу разработчика</li>
                <li>Создайте новое приложение</li>
                <li>Получите Client ID и Client Secret</li>
                <li>Укажите Redirect URI в настройках приложения</li>
                <li>Вставьте ключи в файл .env на сервере</li>
              </ol>

              <div className={styles.envExample}>
                <h4>Пример .env:</h4>
                <pre>{getEnvExample(showConfig)}</pre>
              </div>
            </div>

            <button 
              className={styles.closeButton}
              onClick={() => setShowConfig(null)}
            >
              Закрыть
            </button>
          </div>
        </div>
      )}

      {/* Информация */}
      <div className={styles.info}>
        <h3>💡 Советы</h3>
        <ul>
          <li>
            <strong>Spotify</strong> — основной источник с самой большой библиотекой
          </li>
          <li>
            <strong>SoundCloud</strong> — отлично подходит для ремиксов и независимых артистов
          </li>
          <li>
            <strong>Navidrome</strong> — используйте для вашей личной коллекции в lossless
          </li>
          <li>
            <strong>AI сервисы</strong> — генерируйте уникальную музыку по промпту
          </li>
        </ul>
      </div>
    </div>
  );
}

function getEnvExample(sourceId) {
  const examples = {
    spotify: `SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret`,
    
    soundcloud: `SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret`,
    
    navidrome: `NAVIDROME_URL=http://localhost:4533
NAVIDROME_USERNAME=your_username
NAVIDROME_PASSWORD=your_password`,
    
    vk: `VK_CLIENT_ID=your_client_id
VK_CLIENT_SECRET=your_client_secret`,
    
    youtube: `YOUTUBE_API_KEY=your_api_key`,
    
    ai: `SUNO_API_KEY=your_api_key
MUBERT_TOKEN=your_token
LALAL_API_KEY=your_api_key
ELEVENLABS_API_KEY=your_api_key`,
  };
  
  return examples[sourceId] || '# Настройка зависит от сервиса';
}
