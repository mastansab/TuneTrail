import { useEffect, useId, useState } from 'react';
import { Activity, Save } from 'lucide-react';
import { apiRequest } from '../api/client';

export default function ProfileView({
  user,
  preferences,
  genres,
  onSaveProfile,
}) {
  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [selectedGenres, setSelectedGenres] = useState(preferences?.preferred_genres || []);
  const [hybridAlpha, setHybridAlpha] = useState(preferences?.hybrid_alpha ?? 0.6);
  const [saving, setSaving] = useState(false);
  const [evalMetrics, setEvalMetrics] = useState(null);
  const [health, setHealth] = useState(null);

  const nameId = useId();
  const alphaId = useId();

  useEffect(() => {
    setDisplayName(user?.display_name || '');
    setSelectedGenres(preferences?.preferred_genres || []);
    setHybridAlpha(preferences?.hybrid_alpha ?? 0.6);
  }, [user, preferences]);

  useEffect(() => {
    apiRequest('/recommendations/evaluate').then(setEvalMetrics).catch(() => {});
    apiRequest('/health').then(setHealth).catch(() => {});
  }, []);

  function toggleGenre(g) {
    setSelectedGenres((prev) =>
      prev.includes(g) ? prev.filter((item) => item !== g) : [...prev, g]
    );
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await onSaveProfile({
        display_name: displayName,
        preferred_genres: selectedGenres,
        hybrid_alpha: hybridAlpha,
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <h1>Profile &amp; System Monitoring</h1>
          <p className="page-subtitle">
            Manage your listener preferences and inspect live AI evaluation &amp; health metrics.
          </p>
        </div>
      </header>

      <div className="dashboard-panels">
        <section className="panel">
          <h2 className="panel-title">Listener Preferences</h2>
          <form onSubmit={handleSave}>
            <div className="form-group">
              <label htmlFor={nameId} className="form-label">
                Display Name
              </label>
              <input
                id={nameId}
                className="input"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <span className="form-label">Preferred Genres (Cold-Start &amp; Content Weighting)</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {genres.map((g) => {
                  const active = selectedGenres.includes(g);
                  return (
                    <button
                      key={g}
                      type="button"
                      className="btn"
                      aria-pressed={active}
                      onClick={() => toggleGenre(g)}
                      style={{
                        padding: '6px 12px',
                        minBlockSize: 32,
                        fontSize: '0.82rem',
                        borderColor: active ? 'var(--accent-teal)' : undefined,
                        background: active ? 'rgba(20,184,166,0.18)' : undefined,
                      }}
                    >
                      {g}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor={alphaId} className="form-label">
                Default Hybrid Alpha (&alpha; = {Number(hybridAlpha).toFixed(2)})
              </label>
              <input
                id={alphaId}
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={hybridAlpha}
                onChange={(e) => setHybridAlpha(parseFloat(e.target.value))}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={saving}>
              <Save size={16} aria-hidden="true" /> {saving ? 'Saving...' : 'Save Preferences'}
            </button>
          </form>
        </section>

        <section className="panel">
          <h2 className="panel-title">
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={18} aria-hidden="true" /> AI Model &amp; System Monitoring
            </span>
            <span
              className="chip"
              style={{
                borderColor: health?.status === 'healthy' ? 'var(--accent-teal)' : undefined,
                color: health?.status === 'healthy' ? 'var(--accent-teal-bright)' : undefined,
              }}
            >
              {health?.status || 'checking...'}
            </span>
          </h2>

          {evalMetrics ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="kpi-card" style={{ padding: 14 }}>
                <div>
                  <div className="kpi-value" style={{ fontSize: '1.4rem' }}>
                    {(evalMetrics.hit_rate_at_k * 100).toFixed(1)}%
                  </div>
                  <div className="kpi-label">Hit Rate @{evalMetrics.k}</div>
                </div>
              </div>
              <div className="kpi-card" style={{ padding: 14 }}>
                <div>
                  <div className="kpi-value" style={{ fontSize: '1.4rem' }}>
                    {(evalMetrics.recall_at_k * 100).toFixed(1)}%
                  </div>
                  <div className="kpi-label">Recall @{evalMetrics.k}</div>
                </div>
              </div>
              <div className="kpi-card" style={{ padding: 14 }}>
                <div>
                  <div className="kpi-value" style={{ fontSize: '1.4rem' }}>
                    {(evalMetrics.catalog_coverage * 100).toFixed(1)}%
                  </div>
                  <div className="kpi-label">Catalog Coverage</div>
                </div>
              </div>
              <div className="kpi-card" style={{ padding: 14 }}>
                <div>
                  <div className="kpi-value" style={{ fontSize: '1.4rem' }}>
                    {evalMetrics.avg_genre_diversity}
                  </div>
                  <div className="kpi-label">Avg Genres / Top-10</div>
                </div>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)' }}>Loading evaluation metrics...</p>
          )}
        </section>
      </div>
    </div>
  );
}
