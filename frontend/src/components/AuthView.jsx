import { useId, useState } from 'react';
import { Disc3, Sparkles } from 'lucide-react';
import { apiRequest, setToken } from '../api/client';

const GENRES = [
  'Synthwave',
  'Electronic',
  'Lo-Fi',
  'Ambient',
  'Jazz Fusion',
  'Indie Pop',
  'Alt Rock',
  'R&B Soul',
];

export default function AuthView({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [identifier, setIdentifier] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [preferredGenres, setPreferredGenres] = useState(['Synthwave', 'Lo-Fi']);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const idPrefix = useId();

  function toggleGenre(genre) {
    setPreferredGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register';
      const body =
        mode === 'login'
          ? { identifier, password }
          : {
              username,
              email,
              display_name: displayName || username,
              password,
              preferred_genres: preferredGenres,
            };

      const res = await apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      setToken(res.token);
      onAuthenticated(res.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function fillDemoAccount() {
    setMode('login');
    setIdentifier('demo@tunetrail.ai');
    setPassword('Demo@1234');
    setError('');
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <div className="brand" style={{ padding: 0, marginBottom: 20 }}>
          <div className="brand-logo">
            <Disc3 size={22} aria-hidden="true" />
          </div>
          <div>
            <div className="brand-title">TuneTrail</div>
            <div className="brand-sub">AI Music Discovery</div>
          </div>
        </div>

        <h1 style={{ fontSize: '1.5rem', marginBottom: 6 }}>
          {mode === 'login' ? 'Welcome back' : 'Create your listener profile'}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 20 }}>
          {mode === 'login'
            ? 'Sign in to access hybrid AI recommendations and your playlists.'
            : 'Personalize your music discovery with Content & Collaborative AI.'}
        </p>

        {error && (
          <div
            role="alert"
            style={{
              background: 'rgba(244, 63, 94, 0.14)',
              border: '1px solid rgba(244, 63, 94, 0.4)',
              color: '#fda4af',
              padding: '10px 12px',
              borderRadius: 8,
              marginBottom: 16,
              fontSize: '0.88rem',
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {mode === 'login' ? (
            <div className="form-group">
              <label htmlFor={`${idPrefix}-identifier`} className="form-label">
                Username or Email
              </label>
              <input
                id={`${idPrefix}-identifier`}
                className="input"
                type="text"
                autoComplete="username"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
              />
            </div>
          ) : (
            <>
              <div className="form-group">
                <label htmlFor={`${idPrefix}-username`} className="form-label">
                  Username
                </label>
                <input
                  id={`${idPrefix}-username`}
                  className="input"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor={`${idPrefix}-email`} className="form-label">
                  Email
                </label>
                <input
                  id={`${idPrefix}-email`}
                  className="input"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor={`${idPrefix}-display`} className="form-label">
                  Display Name
                </label>
                <input
                  id={`${idPrefix}-display`}
                  className="input"
                  type="text"
                  autoComplete="name"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor={`${idPrefix}-password`} className="form-label">
              Password
            </label>
            <span id={`${idPrefix}-pwd-hint`} className="form-hint">
              Minimum 6 characters.
            </span>
            <input
              id={`${idPrefix}-password`}
              className="input"
              type="password"
              aria-describedby={`${idPrefix}-pwd-hint`}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <span className="form-label">Starter Genres (helps cold-start AI)</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {GENRES.map((g) => {
                  const selected = preferredGenres.includes(g);
                  return (
                    <button
                      key={g}
                      type="button"
                      className="btn"
                      aria-pressed={selected}
                      onClick={() => toggleGenre(g)}
                      style={{
                        padding: '6px 12px',
                        minBlockSize: 32,
                        fontSize: '0.8rem',
                        borderColor: selected ? 'var(--accent-teal)' : undefined,
                        background: selected ? 'rgba(20,184,166,0.18)' : undefined,
                      }}
                    >
                      {g}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 6 }}
            disabled={loading}
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 16 }}>
          <button type="button" className="btn btn-teal" onClick={fillDemoAccount}>
            <Sparkles size={16} aria-hidden="true" /> Fill Demo Listener (demo@tunetrail.ai)
          </button>

          <button
            type="button"
            className="btn"
            onClick={() => {
              setMode((m) => (m === 'login' ? 'register' : 'login'));
              setError('');
            }}
          >
            {mode === 'login'
              ? 'New to TuneTrail? Register an account'
              : 'Already have an account? Sign in'}
          </button>
        </div>
      </section>
    </main>
  );
}
