import React, { useContext, useEffect, useRef } from 'react';
import { PlayerContext } from '../contexts/PlayerContext';

const Crossfade = ({ enabled, duration = 5000 }) => {
  const { audioElement, nextTrack, currentTrack, queue } = useContext(PlayerContext);
  const crossfadeTimeoutRef = useRef(null);
  const originalVolumeRef = useRef(1);

  useEffect(() => {
    if (!audioElement || !enabled || !currentTrack) return;

    const handleTimeUpdate = () => {
      const remaining = audioElement.duration - audioElement.currentTime;
      
      if (remaining <= duration / 1000 && remaining > 0) {
        // Начинаем кроссфейд
        const fadeOut = () => {
          const fadeStep = 0.1;
          const currentVolume = audioElement.volume;
          
          if (currentVolume > fadeStep) {
            audioElement.volume = currentVolume - fadeStep;
            setTimeout(fadeOut, duration / 10);
          } else {
            // Переключаем трек
            nextTrack();
            audioElement.volume = 0;
            
            // Плавное увеличение громкости нового трека
            setTimeout(() => {
              const fadeIn = () => {
                const newVolume = audioElement.volume + fadeStep;
                if (newVolume <= originalVolumeRef.current) {
                  audioElement.volume = newVolume;
                  setTimeout(fadeIn, duration / 10);
                }
              };
              fadeIn();
            }, 100);
          }
        };
        
        fadeOut();
      }
    };

    audioElement.addEventListener('timeupdate', handleTimeUpdate);
    
    return () => {
      audioElement.removeEventListener('timeupdate', handleTimeUpdate);
      if (crossfadeTimeoutRef.current) {
        clearTimeout(crossfadeTimeoutRef.current);
      }
    };
  }, [audioElement, enabled, duration, currentTrack, nextTrack]);

  return null;
};

export default Crossfade;
