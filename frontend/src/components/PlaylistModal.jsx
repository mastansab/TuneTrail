import { useEffect, useId, useRef, useState } from 'react';
import { X } from 'lucide-react';

export default function PlaylistModal({
  track,
  playlists,
  onClose,
  onSelectPlaylist,
  onCreatePlaylist,
}) {
  const dialogRef = useRef(null);
  const titleId = useId();
  const inputId = useId();
  const [newName, setNewName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (track && !dialog.open) {
      dialog.showModal();
    } else if (!track && dialog.open) {
      dialog.close();
    }
  }, [track]);

  async function handleCreateAndAdd(e) {
    e.preventDefault();
    if (!newName.trim() || !track) return;
    setCreating(true);
    try {
      const created = await onCreatePlaylist(newName.trim(), '');
      if (created?.id) {
        await onSelectPlaylist(created.id, track.id);
      }
      setNewName('');
      onClose();
    } finally {
      setCreating(false);
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className="modal"
      aria-labelledby={titleId}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
    >
      {track && (
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 16,
            }}
          >
            <h2 id={titleId} style={{ fontSize: '1.2rem' }}>
              Add &ldquo;{track.title}&rdquo; to Playlist
            </h2>
            <button
              type="button"
              className="btn btn-icon"
              onClick={onClose}
              aria-label="Close modal"
            >
              <X size={16} aria-hidden="true" />
            </button>
          </div>

          {playlists.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 18 }}>
              {playlists.map((pl) => (
                <button
                  key={pl.id}
                  type="button"
                  className="btn"
                  style={{ justifyContent: 'space-between' }}
                  onClick={async () => {
                    await onSelectPlaylist(pl.id, track.id);
                    onClose();
                  }}
                >
                  <span>{pl.name}</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {pl.track_count} tracks
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', marginBottom: 14, fontSize: '0.9rem' }}>
              You don&apos;t have any playlists yet. Create one below.
            </p>
          )}

          <form onSubmit={handleCreateAndAdd}>
            <div className="form-group">
              <label htmlFor={inputId} className="form-label">
                Or create a new playlist
              </label>
              <input
                id={inputId}
                className="input"
                type="text"
                placeholder="e.g., Late Night Focus"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? 'Creating...' : 'Create & Add Track'}
            </button>
          </form>
        </div>
      )}
    </dialog>
  );
}
