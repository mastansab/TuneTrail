import { useId } from 'react';
import { Search } from 'lucide-react';
import TrackCard from './TrackCard';

export default function LibraryView({
  tracks,
  genres,
  artists,
  filters,
  onFilterChange,
  onPlay,
  onToggleFavourite,
  onAddToPlaylist,
  title = 'Music Library',
  subtitle = 'Search, filter by artist or genre, play tracks, and save favourites.',
}) {
  const searchId = useId();
  const genreId = useId();
  const artistId = useId();
  const sortId = useId();

  return (
    <div>
      <header className="page-header">
        <div>
          <h1>{title}</h1>
          <p className="page-subtitle">{subtitle}</p>
        </div>
        <span className="chip">{tracks.length} tracks</span>
      </header>

      {onFilterChange && (
        <section className="filter-bar" aria-label="Filter tracks">
          <div style={{ flex: '1 1 220px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={searchId} className="form-label">
              Search Title or Tags
            </label>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Search
                size={16}
                aria-hidden="true"
                style={{ position: 'absolute', left: 10, color: 'var(--text-muted)' }}
              />
              <input
                id={searchId}
                className="input"
                type="search"
                style={{ width: '100%', paddingLeft: 32 }}
                placeholder="Search song title, artist, or mood..."
                value={filters.q}
                onChange={(e) => onFilterChange({ ...filters, q: e.target.value })}
              />
            </div>
          </div>

          <div style={{ flex: '0 1 170px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={genreId} className="form-label">
              Genre
            </label>
            <select
              id={genreId}
              className="select"
              value={filters.genre}
              onChange={(e) => onFilterChange({ ...filters, genre: e.target.value })}
            >
              <option value="all">All Genres</option>
              {genres.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: '0 1 190px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={artistId} className="form-label">
              Artist
            </label>
            <select
              id={artistId}
              className="select"
              value={filters.artist}
              onChange={(e) => onFilterChange({ ...filters, artist: e.target.value })}
            >
              <option value="all">All Artists</option>
              {artists.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: '0 1 160px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label htmlFor={sortId} className="form-label">
              Sort By
            </label>
            <select
              id={sortId}
              className="select"
              value={filters.sort}
              onChange={(e) => onFilterChange({ ...filters, sort: e.target.value })}
            >
              <option value="popularity">Popularity</option>
              <option value="title">Title (A–Z)</option>
              <option value="artist">Artist (A–Z)</option>
              <option value="newest">Newest Release</option>
              <option value="tempo">Tempo (BPM)</option>
            </select>
          </div>
        </section>
      )}

      {tracks.length > 0 ? (
        <div className="tracks-grid">
          {tracks.map((track) => (
            <TrackCard
              key={track.id}
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
            No tracks match your current search or filter criteria.
          </p>
        </div>
      )}
    </div>
  );
}
