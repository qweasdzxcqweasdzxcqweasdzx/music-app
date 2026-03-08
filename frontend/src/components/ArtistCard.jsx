import { useNavigate } from 'react-router-dom';
import styles from './ArtistCard.module.css';

export default function ArtistCard({ artist }) {
  const navigate = useNavigate();

  const handleClick = () => {
    const slug = artist.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    navigate(`/artist/${slug || 'default'}`);
  };

  return (
    <div className={styles.card} onClick={handleClick}>
      <div className={styles.coverWrapper}>
        <img 
          src={artist.cover || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23282828" width="100" height="100"/></svg>'} 
          alt={artist.name}
          className={styles.cover}
        />
      </div>
      
      <div className={styles.info}>
        <div className={styles.name}>{artist.name}</div>
        <div className={styles.type}>Исполнитель</div>
      </div>
    </div>
  );
}
