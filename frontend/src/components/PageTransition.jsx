import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import styles from './PageTransition.module.css';

export default function PageTransition({ children, delay = 300 }) {
  const [isAnimating, setIsAnimating] = useState(true);
  const location = useLocation();

  useEffect(() => {
    setIsAnimating(true);
    const timer = setTimeout(() => {
      setIsAnimating(false);
    }, delay);

    return () => clearTimeout(timer);
  }, [location.pathname, delay]);

  return (
    <div className={`${styles.page} ${isAnimating ? styles.animating : styles.visible}`}>
      {children}
    </div>
  );
}
