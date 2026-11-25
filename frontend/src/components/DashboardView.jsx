import { Disc3, Heart, Headphones, ListMusic, Sparkles } from 'lucide-react';
import TrackCard from './TrackCard';

export default function DashboardView({
  data,
  onPlay,
  onToggleFavourite,
  onAddToPlaylist,
  onNavigate,
}) {
  if (!data) {
    return <p style={{ color: 'var(--text-secondary)' }}>Loading dashboard...</p>;
  }

  const { summary, genre_distribution, listening_activity, recently_played, recommendations } = data;
  const maxGenre = Math.max(1, ...(genre_distribution || []).map((g) => g.count));
  const maxDay = Math.max(1, ...(listening_activity || []).map((d) => d.plays));

  return (
    <div>
      <header className="page-header">
        <div>
          <h1>Listener Dashboard</h1>
          <p className="page-subtitle">
            Your listening footprint, genre balance, and real-time hybrid AI picks.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => onNavigate('recommendations')}>
          <Sparkles size={16} aria-hidden="true" /> Open AI Studio
        </button>
      </header>

      <section className="kpi-grid" aria-label="Summary Statistics">
        <div className="kpi-card">
          <div>
            <div className="kpi-value">{summary.total_tracks}</div>
            <div className="kpi-label">Available Tracks</div>
          </div>
          <div className="kpi-icon">
            <Disc3 size={22} aria-hidden="true" />
          </div>
        </div>

        <div className="kpi-card">
          <div>
            <div className="kpi-value">{summary.total_playlists}</div>
            <div className="kpi-label">Your Playlists</div>
          </div>
          <div className="kpi-icon" style={{ color: 'var(--accent-teal-bright)', background: 'rgba(20,184,166,0.16)' }}>
            <ListMusic size={22} aria-hidden="true" />
          </div>
        </div>

        <div className="kpi-card">
          <div>
            <div className="kpi-value">{summary.total_favourites}</div>
            <div className="kpi-label">Favourite Songs</div>
          </div>
          <div className="kpi-icon" style={{ color: '#fb7185', background: 'rgba(244,63,94,0.16)' }}>
            <Heart size={22} aria-hidden="true" />
          </div>
        </div>

        <div className="kpi-card">
          <div>
            <div className="kpi-value">{summary.total_plays}</div>
            <div className="kpi-label">Total Plays</div>
          </div>
          <div className="kpi-icon" style={{ color: '#fbbf24', background: 'rgba(245,158,11,0.16)' }}>
            <Headphones size={22} aria-hidden="true" />
          </div>
        </div>
      </section>

      <section className="dashboard-panels">
        <div className="panel">
          <h2 className="panel-title">
            <span>Genre Distribution</span>
            <span className="chip">
              {data.genre_source === 'user_history' ? 'Your Plays' : 'Catalog'}
            </span>
          </h2>
          {genre_distribution.map((item) => (
            <div key={item.genre} className="bar-row">
              <span>{item.genre}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.round((item.count / maxGenre) * 100)}%` }}
                />
              </div>
              <span style={{ textAlign: 'end', color: 'var(--text-secondary)' }}>{item.count}</span>
            </div>
          ))}
        </div>

        <div className="panel">
          <h2 className="panel-title">
            <span>Listening Activity</span>
            <span className="chip">Recent Days</span>
          </h2>
          {listening_activity.length > 0 ? (
            listening_activity.map((day) => (
              <div key={day.day} className="bar-row">
                <span style={{ fontSize: '0.8rem' }}>{day.day}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${Math.round((day.plays / maxDay) * 100)}%`,
                      background: 'linear-gradient(90deg, var(--accent-teal), var(--accent-purple))',
                    }}
                  />
                </div>
                <span style={{ textAlign: 'end', color: 'var(--text-secondary)' }}>{day.plays}</span>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Play any track in the Music Library to start building your listening activity timeline.
            </p>
          )}
        </div>
      </section>

      <section style={{ marginBottom: 28 }}>
        <div className="page-header" style={{ marginBottom: 14 }}>
          <h2 style={{ fontSize: '1.25rem' }}>Personalized AI Picks</h2>
          <button type="button" className="btn" onClick={() => onNavigate('recommendations')}>
            See all &amp; tune weights
          </button>
        </div>
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
      </section>

      <section>
        <div className="page-header" style={{ marginBottom: 14 }}>
          <h2 style={{ fontSize: '1.25rem' }}>Recently Played</h2>
          <button type="button" className="btn" onClick={() => onNavigate('history')}>
            Full History
          </button>
        </div>
        {recently_played.length > 0 ? (
          <div className="tracks-grid">
            {recently_played.map((track) => (
              <TrackCard
                key={`${track.event_id}-${track.id}`}
                track={track}
                onPlay={onPlay}
                onToggleFavourite={onToggleFavourite}
                onAddToPlaylist={onAddToPlaylist}
              />
            ))}
          </div>
        ) : (
          <div className="panel">
            <p style={{ color: 'var(--text-secondary)' }}>
              No tracks played yet. Head over to the Music Library to play your first track!
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
