import styles from './AlbumCard.module.css';

export default function AlbumCard({ item, type = 'album' }) {
  return (
    <div className={styles.card}>
      <div className={styles.coverWrapper}>
        <img 
          src={item.cover || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23282828" width="100" height="100"/></svg>'} 
          alt={item.title}
          className={styles.cover}
        />
      </div>
      
      <div className={styles.info}>
        <div className={styles.title}>{item.title}</div>
        <div className={styles.subtitle}>
          {type === 'album' ? item.artist : `${item.count} треков`}
        </div>
      </div>
    </div>
  );
}
