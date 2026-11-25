import { Play } from 'lucide-react';

export default function HistoryView({ history, onPlay }) {
  return (
    <div>
      <header className="page-header">
        <div>
          <h1>Listening History</h1>
          <p className="page-subtitle">
            Every play updates your Content-Based &amp; Collaborative AI taste profile.
          </p>
        </div>
        <span className="chip">{history.length} recent events</span>
      </header>

      {history.length > 0 ? (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">Track</th>
                <th scope="col">Artist</th>
                <th scope="col">Genre</th>
                <th scope="col">Played At</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.event_id}>
                  <td style={{ fontWeight: 600 }}>{item.title}</td>
                  <td>{item.artist}</td>
                  <td>
                    <span className="chip">{item.genre}</span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.84rem' }}>
                    {item.played_at}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-icon"
                      onClick={() => onPlay(item)}
                      aria-label={`Replay ${item.title}`}
                    >
                      <Play size={14} aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="panel">
          <p style={{ color: 'var(--text-secondary)' }}>
            Your listening history is empty. Play tracks in the library to record events.
          </p>
        </div>
      )}
    </div>
  );
}
