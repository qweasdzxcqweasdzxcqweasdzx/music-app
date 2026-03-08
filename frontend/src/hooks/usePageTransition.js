import { useState, useEffect } from 'react';

export function usePageTransition(delay = 300) {
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsAnimating(false);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  return isAnimating;
}

export function useFadeIn(delay = 100) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  return isVisible;
}
