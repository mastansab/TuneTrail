import { useEffect, useState } from 'react';
import { Heart, Pause, Play, SkipForward } from 'lucide-react';

export default function PlayerBar({ currentTrack, onToggleFavourite, onNext }) {
  const [playing, setPlaying] = useState(true);
  const [progress, setProgress] = useState(18);

  useEffect(() => {
    if (!currentTrack) return;
    setPlaying(true);
    setProgress(12);
  }, [currentTrack?.id]);

  useEffect(() => {
    if (!currentTrack || !playing) return undefined;
    const timer = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 0 : prev + 2));
    }, 1000);
    return () => clearInterval(timer);
  }, [currentTrack, playing]);

  if (!currentTrack) return null;

  return (
    <aside className="player-bar" aria-label="Now Playing">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
        <div
          style={{
            width: 46,
            height: 46,
            borderRadius: 10,
            background: `linear-gradient(135deg, ${currentTrack.cover_color || '#7c3aed'}, #0f172a)`,
            flexShrink: 0,
          }}
        />
        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {currentTrack.title}
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            {currentTrack.artist} &bull; {currentTrack.genre}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: '0 1 380px' }}>
        <button
          type="button"
          className="btn btn-primary btn-icon"
          onClick={() => setPlaying((p) => !p)}
          aria-label={playing ? 'Pause playback' : 'Resume playback'}
        >
          {playing ? <Pause size={16} aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
        </button>

        <div className="bar-track" style={{ flex: 1, height: 6 }} aria-hidden="true">
          <div className="bar-fill" style={{ width: `${progress}%` }} />
        </div>

        <button
          type="button"
          className="btn btn-icon"
          onClick={onNext}
          aria-label="Play next track"
        >
          <SkipForward size={16} aria-hidden="true" />
        </button>
      </div>

      <button
        type="button"
        className="btn btn-icon"
        onClick={() => onToggleFavourite(currentTrack)}
        aria-label={currentTrack.is_favourite ? 'Remove from favourites' : 'Add to favourites'}
        aria-pressed={Boolean(currentTrack.is_favourite)}
        style={currentTrack.is_favourite ? { color: '#f43f5e' } : undefined}
      >
        <Heart
          size={18}
          fill={currentTrack.is_favourite ? 'currentColor' : 'none'}
          aria-hidden="true"
        />
      </button>
    </aside>
  );
}
