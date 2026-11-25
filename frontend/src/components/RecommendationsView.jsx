import { useId } from 'react';
import { RefreshCw, Sliders } from 'lucide-react';
import TrackCard from './TrackCard';

export default function RecommendationsView({
  recommendations,
  meta,
  mode,
  alpha,
  excludeRecent,
  onChangeMode,
  onChangeAlpha,
  onToggleExcludeRecent,
  onRefresh,
  onPlay,
  onToggleFavourite,
  onAddToPlaylist,
}) {
  const alphaId = useId();
  const recentId = useId();

  return (
    <div>
      <header className="page-header">
        <div>
          <h1>AI Recommendation Studio</h1>
          <p className="page-subtitle">
            Hybrid Content-Based &amp; Collaborative Filtering with diversity &amp; anti-repetition.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={onRefresh}>
          <RefreshCw size={16} aria-hidden="true" /> Refresh Picks
        </button>
      </header>

      <section className="panel" style={{ marginBottom: 22 }} aria-label="Recommendation Controls">
        <div className="panel-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sliders size={18} aria-hidden="true" /> Algorithm Controls
          </span>
          {meta && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              <span className="chip">Effective &alpha;: {meta.effective_alpha}</span>
              <span className="chip">Similar Listeners: {meta.neighbor_count}</span>
              <span className="chip">Genres in Top-K: {meta.diversity_genres}</span>
              {meta.cold_start && (
                <span className="chip" style={{ borderColor: 'var(--accent-amber)', color: '#fbbf24' }}>
                  Cold-Start Fallback Active
                </span>
              )}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 18, alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: 8 }} role="group" aria-label="Recommendation mode">
            {[
              { id: 'hybrid', label: 'Hybrid' },
              { id: 'content', label: 'Content-Based' },
              { id: 'collaborative', label: 'Collaborative' },
            ].map((m) => (
              <button
                key={m.id}
                type="button"
                className={`btn ${mode === m.id ? 'btn-primary' : ''}`}
                aria-pressed={mode === m.id}
                onClick={() => onChangeMode(m.id)}
              >
                {m.label}
              </button>
            ))}
          </div>

          <div style={{ flex: '1 1 240px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={alphaId} className="form-label">
              Content vs Collaborative Weight (&alpha; = {alpha.toFixed(2)})
            </label>
            <input
              id={alphaId}
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={alpha}
              disabled={mode !== 'hybrid'}
              onChange={(e) => onChangeAlpha(parseFloat(e.target.value))}
            />
          </div>

          <label htmlFor={recentId} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input
              id={recentId}
              type="checkbox"
              checked={excludeRecent}
              onChange={(e) => onToggleExcludeRecent(e.target.checked)}
            />
            <span>Avoid recently played tracks</span>
          </label>
        </div>
      </section>

      <div className="tracks-grid">
        {recommendations.map((track) => (
          <TrackCard
            key={track.id}
            track={track}
            onPlay={onPlay}
            onToggleFavourite={onToggleFavourite}
            onAddToPlaylist={onAddToPlaylist}
            showExplanation
          />
        ))}
      </div>
    </div>
  );
}
