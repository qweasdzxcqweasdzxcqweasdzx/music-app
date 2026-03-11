import React, { useState, useEffect } from 'react';
import { musicAPI } from '../api/musicApi';
import styles from './VersionSwitcher.module.css';

/**
 * VersionSwitcher - Компонент переключения между censored/uncensored версиями трека
 */
const VersionSwitcher = ({ track, onVersionChange }) => {
  const [isExplicit, setIsExplicit] = useState(false);
  const [hasUncensored, setHasUncensored] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uncensoredTrack, setUncensoredTrack] = useState(null);

  useEffect(() => {
    checkCensorship();
  }, [track]);

  const checkCensorship = async () => {
    if (!track) return;

    try {
      const info = await musicAPI.getTrackCensorshipInfo(track.id, track.title, track.artist);
      setIsExplicit(info.is_explicit || false);
      setHasUncensored(info.has_uncensored_in_db || false);
    } catch (error) {
      console.error('Error checking censorship:', error);
    }
  };

  const findUncensored = async () => {
    if (!track) return;

    setLoading(true);
    try {
      const result = await musicAPI.findUncensoredVersion(track.id, track.title, track.artist, track.source);

      if (result.status === 'found') {
        setUncensoredTrack(result.track);
        setHasUncensored(true);

        // Уведомляем родительский компонент
        if (onVersionChange) {
          onVersionChange({
            type: 'uncensored_found',
            original: track,
            uncensored: result.track,
            source: result.source,
            confidence: result.confidence
          });
        }
      }
    } catch (error) {
      console.error('Error finding uncensored version:', error);
    } finally {
      setLoading(false);
    }
  };

  const switchToExplicit = () => {
    if (uncensoredTrack && onVersionChange) {
      onVersionChange({
        type: 'switch_to_explicit',
        original: track,
        uncensored: uncensoredTrack
      });
      setIsExplicit(true);
    }
  };

  const switchToClean = () => {
    if (onVersionChange) {
      onVersionChange({
        type: 'switch_to_clean',
        track: track
      });
      setIsExplicit(false);
    }
  };

  // Если трек уже explicit, показываем метку
  if (isExplicit) {
    return (
      <div className={styles.explicitBadge}>
        <span className={styles.badge}>EXPLICIT</span>
      </div>
    );
  }

  // Если есть uncensored версия, показываем переключатель
  if (hasUncensored && uncensoredTrack) {
    return (
      <div className={styles.switcher}>
        <button
          className={`${styles.versionBtn} ${!isExplicit ? styles.active : ''}`}
          onClick={switchToClean}
        >
          Clean
        </button>
        <button
          className={`${styles.versionBtn} ${isExplicit ? styles.active : ''}`}
          onClick={switchToExplicit}
        >
          Explicit
        </button>
      </div>
    );
  }

  // Кнопка поиска uncensored версии
  return (
    <div className={styles.findContainer}>
      <button
        className={styles.findBtn}
        onClick={findUncensored}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className={styles.spinner}></span>
            Поиск оригинала...
          </>
        ) : (
          <>
            <svg viewBox="0 0 16 16" width="16" height="16">
              <path fill="currentColor" d="M10.53 2a8.53 8.53 0 0 1 6.97 13.47l5.3 5.3-1.42 1.42-5.3-5.3A8.53 8.53 0 1 1 10.53 2m0 2a6.53 6.53 0 1 0 0 13.06 6.53 6.53 0 0 0 0-13.06z"/>
            </svg>
            Найти без цензуры
          </>
        )}
      </button>
    </div>
  );
};

export default VersionSwitcher;
