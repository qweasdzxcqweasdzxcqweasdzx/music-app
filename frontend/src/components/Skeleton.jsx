import styles from './Skeleton.module.css';

/**
 * Skeleton loader для контента
 * Как в Spotify - показывает анимацию загрузки
 */

export function SkeletonTrack() {
  return (
    <div className={styles.trackSkeleton}>
      <div className={styles.coverSkeleton}></div>
      <div className={styles.info}>
        <div className={styles.titleSkeleton}></div>
        <div className={styles.artistSkeleton}></div>
      </div>
      <div className={styles.durationSkeleton}></div>
    </div>
  );
}

export function SkeletonArtist() {
  return (
    <div className={styles.artistCardSkeleton}>
      <div className={styles.artistImageSkeleton}></div>
      <div className={styles.artistNameSkeleton}></div>
    </div>
  );
}

export function SkeletonAlbum() {
  return (
    <div className={styles.albumCardSkeleton}>
      <div className={styles.albumCoverSkeleton}></div>
      <div className={styles.albumTitleSkeleton}></div>
      <div className={styles.albumArtistSkeleton}></div>
    </div>
  );
}

export function SkeletonSection({ title = true }) {
  return (
    <section className={styles.sectionSkeleton}>
      {title && <div className={styles.sectionTitleSkeleton}></div>}
      <div className={styles.sectionContentSkeleton}>
        <SkeletonTrack />
        <SkeletonTrack />
        <SkeletonTrack />
        <SkeletonTrack />
      </div>
    </section>
  );
}

export default function Skeleton({ type = 'track', count = 4 }) {
  const skeletons = [];
  
  for (let i = 0; i < count; i++) {
    switch (type) {
      case 'track':
        skeletons.push(<SkeletonTrack key={i} />);
        break;
      case 'artist':
        skeletons.push(<SkeletonArtist key={i} />);
        break;
      case 'album':
        skeletons.push(<SkeletonAlbum key={i} />);
        break;
      case 'section':
        return <SkeletonSection key={i} />;
      default:
        skeletons.push(<SkeletonTrack key={i} />);
    }
  }
  
  return <>{skeletons}</>;
}
