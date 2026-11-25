import { Heart, ListPlus, Play } from 'lucide-react';

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = String(seconds % 60).padStart(2, '0');
  return `${mins}:${secs}`;
}

export default function TrackCard({
  track,
  onPlay,
  onToggleFavourite,
  onAddToPlaylist,
  showExplanation = false,
}) {
  const coverStyle = {
    background: `linear-gradient(135deg, ${track.cover_color || '#7c3aed'}, #0f172a)`,
  };

  return (
    <article className="track-card">
      <div className="track-cover" style={coverStyle}>
        <span className="genre-badge">{track.genre}</span>
        {track.scores?.match_percent != null && (
          <span className="match-badge">{track.scores.match_percent}% Match</span>
        )}
      </div>

      <div>
        <h3 className="track-title">{track.title}</h3>
        <p className="track-artist">
          {track.artist} &bull; {track.album}
        </p>
      </div>

      <div className="track-meta">
        <span className="chip">{Math.round(track.tempo)} BPM</span>
        <span className="chip">Energy {Math.round(track.energy * 100)}%</span>
        <span className="chip">{formatDuration(track.duration_sec)}</span>
      </div>

      {showExplanation && track.explanation && (
        <div className="explanation-box">
          <strong>Why this track:</strong> {track.explanation}
          {track.scores && (
            <div style={{ marginTop: 4, fontSize: '0.72rem', color: '#94a3b8' }}>
              CB: {Math.round(track.scores.content * 100)}% &bull; CF:{' '}
              {Math.round(track.scores.collaborative * 100)}%
            </div>
          )}
        </div>
      )}

      <div className="track-actions">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => onPlay(track)}
          aria-label={`Play ${track.title} by ${track.artist}`}
        >
          <Play size={16} aria-hidden="true" /> Play
        </button>

        <div style={{ display: 'flex', gap: 6 }}>
          <button
            type="button"
            className="btn btn-icon"
            onClick={() => onToggleFavourite(track)}
            aria-label={
              track.is_favourite
                ? `Remove ${track.title} from favourites`
                : `Add ${track.title} to favourites`
            }
            aria-pressed={Boolean(track.is_favourite)}
            style={
              track.is_favourite
                ? { color: '#f43f5e', borderColor: 'rgba(244,63,94,0.45)' }
                : undefined
            }
          >
            <Heart
              size={16}
              fill={track.is_favourite ? 'currentColor' : 'none'}
              aria-hidden="true"
            />
          </button>

          <button
            type="button"
            className="btn btn-icon"
            onClick={() => onAddToPlaylist(track)}
            aria-label={`Add ${track.title} to playlist`}
          >
            <ListPlus size={16} aria-hidden="true" />
          </button>
        </div>
      </div>
    </article>
  );
}
