import { useId, useState } from 'react';
import { Play, Plus, Trash2 } from 'lucide-react';

export default function PlaylistsView({
  playlists,
  onCreatePlaylist,
  onDeletePlaylist,
  onRemoveTrack,
  onPlay,
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const nameId = useId();
  const descId = useId();

  async function handleCreate(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      await onCreatePlaylist(name.trim(), description.trim());
      setName('');
      setDescription('');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <h1>Your Playlists</h1>
          <p className="page-subtitle">
            Organize your favorite discoveries into custom collections.
          </p>
        </div>
        <span className="chip">{playlists.length} playlists</span>
      </header>

      <section className="panel" style={{ marginBottom: 24 }}>
        <h2 className="panel-title">Create New Playlist</h2>
        <form
          onSubmit={handleCreate}
          style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'flex-end' }}
        >
          <div style={{ flex: '1 1 200px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={nameId} className="form-label">
              Playlist Name
            </label>
            <input
              id={nameId}
              className="input"
              type="text"
              placeholder="e.g., Synthwave Coding"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div style={{ flex: '2 1 260px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={descId} className="form-label">
              Description (optional)
            </label>
            <input
              id={descId}
              className="input"
              type="text"
              placeholder="Vibe or mood notes..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={creating}>
            <Plus size={16} aria-hidden="true" /> {creating ? 'Creating...' : 'Create Playlist'}
          </button>
        </form>
      </section>

      {playlists.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          {playlists.map((pl) => (
            <article key={pl.id} className="panel">
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 12,
                  marginBottom: 12,
                }}
              >
                <div>
                  <h2 style={{ fontSize: '1.15rem' }}>{pl.name}</h2>
                  {pl.description && (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                      {pl.description}
                    </p>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span className="chip">{pl.track_count} tracks</span>
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={() => onDeletePlaylist(pl.id)}
                    aria-label={`Delete playlist ${pl.name}`}
                  >
                    <Trash2 size={15} aria-hidden="true" /> Delete
                  </button>
                </div>
              </div>

              {pl.tracks.length > 0 ? (
                <div className="table-wrap">
                  <table className="data-table">
                    <caption className="visually-hidden">Tracks in {pl.name}</caption>
                    <thead>
                      <tr>
                        <th scope="col">Title</th>
                        <th scope="col">Artist</th>
                        <th scope="col">Genre</th>
                        <th scope="col">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pl.tracks.map((t) => (
                        <tr key={t.id}>
                          <td>{t.title}</td>
                          <td>{t.artist}</td>
                          <td>
                            <span className="chip">{t.genre}</span>
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: 8 }}>
                              <button
                                type="button"
                                className="btn btn-icon"
                                onClick={() => onPlay(t)}
                                aria-label={`Play ${t.title}`}
                              >
                                <Play size={14} aria-hidden="true" />
                              </button>
                              <button
                                type="button"
                                className="btn btn-icon btn-danger"
                                onClick={() => onRemoveTrack(pl.id, t.id)}
                                aria-label={`Remove ${t.title} from ${pl.name}`}
                              >
                                <Trash2 size={14} aria-hidden="true" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                  No tracks in this playlist yet. Add songs from the Music Library or AI Studio!
                </p>
              )}
            </article>
          ))}
        </div>
      ) : (
        <div className="panel">
          <p style={{ color: 'var(--text-secondary)' }}>
            You have no playlists yet. Create one above to get started.
          </p>
        </div>
      )}
    </div>
  );
}
