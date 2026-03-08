import { useState, useEffect } from 'react';
import { usePlayer } from '../contexts/PlayerContext';
import { musicAPI } from '../api/musicApi';
import PageTransition from '../components/PageTransition';
import { ClockIcon, FireIcon, StarIcon } from '../components/Icons';
import styles from './Stats.module.css';

export default function Stats() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated } = usePlayer();

  useEffect(() => {
    const loadStats = async () => {
      if (!isAuthenticated) {
        setIsLoading(false);
        return;
      }

      try {
        const [statsData, historyData] = await Promise.all([
          musicAPI.getStats().catch(() => null),
          musicAPI.getHistory(100).catch(() => []),
        ]);

        setStats(statsData);
        setHistory(historyData || []);
      } catch (err) {
        console.error('Error loading stats:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <PageTransition>
        <div className={styles.stats}>
          <div className={styles.notAuth}>
            <h1>Статистика</h1>
            <p>Войдите через Telegram чтобы увидеть статистику прослушиваний</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  if (isLoading) {
    return (
      <PageTransition>
        <div className={styles.stats}>
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>Загрузка статистики...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  const totalPlays = stats?.total_plays || 0;
  const totalMinutes = stats?.total_minutes || 0;
  const totalHours = (totalMinutes / 60).toFixed(1);

  return (
    <PageTransition>
      <div className={styles.stats}>
        <header className={styles.header}>
          <h1 className={styles.title}>Моя статистика</h1>
        </header>

        {/* Общая статистика */}
        <section className={styles.section}>
          <div className={styles.overview}>
            <div className={styles.statCard}>
              <ClockIcon size={32} />
              <div className={styles.statValue}>{totalHours}</div>
              <div className={styles.statLabel}>часов прослушано</div>
            </div>

            <div className={styles.statCard}>
              <FireIcon size={32} />
              <div className={styles.statValue}>{totalPlays}</div>
              <div className={styles.statLabel}>треков сыграно</div>
            </div>

            <div className={styles.statCard}>
              <StarIcon size={32} />
              <div className={styles.statValue}>{history.length > 0 ? '🎵' : '😔'}</div>
              <div className={styles.statLabel}>
                {history.length > 0 ? 'Активный слушатель' : 'Начните слушать музыку'}
              </div>
            </div>
          </div>
        </section>

        {/* Недавняя активность */}
        {history.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Недавние прослушивания</h2>
            <div className={styles.recentList}>
              {history.slice(0, 10).map((item, index) => (
                <div key={item._id || index} className={styles.recentItem}>
                  <div className={styles.recentInfo}>
                    <div className={styles.recentTrack}>Трек #{item.track_id}</div>
                    <div className={styles.recentDate}>
                      {new Date(item.played_at).toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                  <div className={styles.recentDuration}>
                    {Math.floor(item.play_duration / 60)} мин
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Достижения */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Достижения</h2>
          <div className={styles.achievements}>
            <div className={`${styles.achievement} ${totalPlays >= 10 ? styles.unlocked : styles.locked}`}>
              <div className={styles.achievementIcon}>🎵</div>
              <div className={styles.achievementInfo}>
                <div className={styles.achievementTitle}>Новичок</div>
                <div className={styles.achievementDesc}>Прослушать 10 треков</div>
              </div>
            </div>

            <div className={`${styles.achievement} ${totalPlays >= 100 ? styles.unlocked : styles.locked}`}>
              <div className={styles.achievementIcon}>🔥</div>
              <div className={styles.achievementInfo}>
                <div className={styles.achievementTitle}>Любитель</div>
                <div className={styles.achievementDesc}>Прослушать 100 треков</div>
              </div>
            </div>

            <div className={`${styles.achievement} ${totalPlays >= 500 ? styles.unlocked : styles.locked}`}>
              <div className={styles.achievementIcon}>⭐</div>
              <div className={styles.achievementInfo}>
                <div className={styles.achievementTitle}>Фанат</div>
                <div className={styles.achievementDesc}>Прослушать 500 треков</div>
              </div>
            </div>

            <div className={`${styles.achievement} ${totalHours >= 100 ? styles.unlocked : styles.locked}`}>
              <div className={styles.achievementIcon}>🏆</div>
              <div className={styles.achievementInfo}>
                <div className={styles.achievementTitle}>Меломан</div>
                <div className={styles.achievementDesc}>100 часов музыки</div>
              </div>
            </div>
          </div>
        </section>

        <div className={styles.spacer} />
      </div>
    </PageTransition>
  );
}
