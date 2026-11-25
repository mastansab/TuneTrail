import { useCallback, useEffect, useState } from 'react';
import {
  Compass,
  Disc3,
  Heart,
  History,
  LayoutDashboard,
  ListMusic,
  LogOut,
  Sparkles,
  User,
} from 'lucide-react';
import { apiRequest, getToken, setToken } from './api/client';
import AuthView from './components/AuthView';
import DashboardView from './components/DashboardView';
import HistoryView from './components/HistoryView';
import LibraryView from './components/LibraryView';
import PlayerBar from './components/PlayerBar';
import PlaylistModal from './components/PlaylistModal';
import PlaylistsView from './components/PlaylistsView';
import ProfileView from './components/ProfileView';
import RecommendationsView from './components/RecommendationsView';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'library', label: 'Music Library', icon: Compass },
  { id: 'recommendations', label: 'AI For You', icon: Sparkles },
  { id: 'favourites', label: 'Favourites', icon: Heart },
  { id: 'playlists', label: 'Playlists', icon: ListMusic },
  { id: 'history', label: 'History', icon: History },
  { id: 'profile', label: 'Profile & QA', icon: User },
];

export default function App() {
  const [user, setUser] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  const [dashboardData, setDashboardData] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [artists, setArtists] = useState([]);
  const [filters, setFilters] = useState({ q: '', genre: 'all', artist: 'all', sort: 'popularity' });

  const [favourites, setFavourites] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [history, setHistory] = useState([]);

  const [recMode, setRecMode] = useState('hybrid');
  const [recAlpha, setRecAlpha] = useState(0.6);
  const [excludeRecent, setExcludeRecent] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [recMeta, setRecMeta] = useState(null);

  const [currentTrack, setCurrentTrack] = useState(null);
  const [modalTrack, setModalTrack] = useState(null);
  const [toast, setToast] = useState('');

  const showToast = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 2800);
  }, []);

  const loadRecommendations = useCallback(async (mode = recMode, alpha = recAlpha, exRecent = excludeRecent) => {
    const res = await apiRequest(
      `/recommendations?mode=${mode}&alpha=${alpha}&limit=12&exclude_recent=${exRecent}`
    );
    setRecommendations(res.recommendations);
    setRecMeta(res.meta);
  }, [recMode, recAlpha, excludeRecent]);

  const loadTracks = useCallback(async (f = filters) => {
    const params = new URLSearchParams({
      q: f.q,
      genre: f.genre,
      artist: f.artist,
      sort: f.sort,
    });
    const res = await apiRequest(`/tracks?${params.toString()}`);
    setTracks(res.tracks);
  }, [filters]);

  const loadAllUserData = useCallback(async () => {
    const [metaRes, dashRes, favRes, plRes, histRes] = await Promise.all([
      apiRequest('/tracks/meta'),
      apiRequest('/dashboard'),
      apiRequest('/favourites'),
      apiRequest('/playlists'),
      apiRequest('/history'),
    ]);
    setGenres(metaRes.genres);
    setArtists(metaRes.artists);
    setDashboardData(dashRes);
    setFavourites(favRes.favourites);
    setPlaylists(plRes.playlists);
    setHistory(histRes.history);
  }, []);

  useEffect(() => {
    async function initAuth() {
      if (!getToken()) {
        setCheckingAuth(false);
        return;
      }
      try {
        const res = await apiRequest('/auth/me');
        setUser(res.user);
        setPreferences(res.preferences);
        setRecAlpha(res.preferences?.hybrid_alpha ?? 0.6);
      } catch {
        setToken(null);
      } finally {
        setCheckingAuth(false);
      }
    }
    initAuth();
  }, []);

  useEffect(() => {
    if (!user) return;
    loadAllUserData();
    loadTracks(filters);
    loadRecommendations(recMode, recAlpha, excludeRecent);
  }, [user]);

  useEffect(() => {
    if (!user) return;
    loadTracks(filters);
  }, [filters, user, loadTracks]);

  useEffect(() => {
    if (!user) return;
    loadRecommendations(recMode, recAlpha, excludeRecent);
  }, [recMode, recAlpha, excludeRecent, user, loadRecommendations]);

  async function handlePlay(track) {
    setCurrentTrack(track);
    try {
      await apiRequest('/history', {
        method: 'POST',
        body: JSON.stringify({ track_id: track.id, play_duration_sec: track.duration_sec, completed: true }),
      });
      showToast(`Playing "${track.title}" by ${track.artist}`);
      loadAllUserData();
      loadRecommendations();
    } catch (err) {
      showToast(err.message);
    }
  }

  async function handleToggleFavourite(track) {
    try {
      if (track.is_favourite) {
        await apiRequest(`/favourites/${track.id}`, { method: 'DELETE' });
        showToast(`Removed "${track.title}" from favourites`);
      } else {
        await apiRequest('/favourites', {
          method: 'POST',
          body: JSON.stringify({ track_id: track.id }),
        });
        showToast(`Saved "${track.title}" to favourites`);
      }
      if (currentTrack?.id === track.id) {
        setCurrentTrack((prev) => ({ ...prev, is_favourite: !prev.is_favourite }));
      }
      await Promise.all([loadAllUserData(), loadTracks(filters), loadRecommendations()]);
    } catch (err) {
      showToast(err.message);
    }
  }

  async function handleCreatePlaylist(name, description) {
    const res = await apiRequest('/playlists', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
    showToast(`Created playlist "${name}"`);
    await loadAllUserData();
    return res.playlist;
  }

  async function handleDeletePlaylist(playlistId) {
    await apiRequest(`/playlists/${playlistId}`, { method: 'DELETE' });
    showToast('Playlist deleted');
    await loadAllUserData();
  }

  async function handleAddTrackToPlaylist(playlistId, trackId) {
    try {
      await apiRequest(`/playlists/${playlistId}/tracks`, {
        method: 'POST',
        body: JSON.stringify({ track_id: trackId }),
      });
      showToast('Added track to playlist');
      await loadAllUserData();
    } catch (err) {
      showToast(err.message);
    }
  }

  async function handleRemoveTrackFromPlaylist(playlistId, trackId) {
    await apiRequest(`/playlists/${playlistId}/tracks/${trackId}`, { method: 'DELETE' });
    showToast('Removed track from playlist');
    await loadAllUserData();
  }

  async function handleSaveProfile(payload) {
    const res = await apiRequest('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
    setUser(res.user);
    setPreferences(res.preferences);
    setRecAlpha(res.preferences.hybrid_alpha);
    showToast('Preferences saved & AI profile updated');
    await loadRecommendations(recMode, res.preferences.hybrid_alpha, excludeRecent);
  }

  async function handleLogout() {
    await apiRequest('/auth/logout', { method: 'POST' }).catch(() => {});
    setToken(null);
    setUser(null);
    setCurrentTrack(null);
  }

  if (checkingAuth) {
    return (
      <main className="auth-shell">
        <p style={{ color: 'var(--text-secondary)' }}>Loading TuneTrail...</p>
      </main>
    );
  }

  if (!user) {
    return (
      <AuthView
        onAuthenticated={async (u) => {
          setUser(u);
          const me = await apiRequest('/auth/me').catch(() => null);
          if (me?.preferences) {
            setPreferences(me.preferences);
            setRecAlpha(me.preferences.hybrid_alpha ?? 0.6);
          }
        }}
      />
    );
  }

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">
            <Disc3 size={22} aria-hidden="true" />
          </div>
          <div>
            <div className="brand-title">TuneTrail</div>
            <div className="brand-sub">AI Music Engine</div>
          </div>
        </div>

        <nav aria-label="Primary">
          <ul className="nav-list">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className={`nav-btn ${activeTab === item.id ? 'active' : ''}`}
                    aria-current={activeTab === item.id ? 'page' : undefined}
                    onClick={() => setActiveTab(item.id)}
                  >
                    <Icon size={18} aria-hidden="true" />
                    <span>{item.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="user-pill">
            <div className="avatar-circle">
              {(user.display_name || user.username || 'U')[0].toUpperCase()}
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontWeight: 600, fontSize: '0.88rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user.display_name}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>@{user.username}</div>
            </div>
          </div>
          <button type="button" className="btn" onClick={handleLogout}>
            <LogOut size={16} aria-hidden="true" /> Sign Out
          </button>
        </div>
      </aside>

      <main id="main-content" className="main-content" tabIndex={-1}>
        {activeTab === 'dashboard' && (
          <DashboardView
            data={dashboardData}
            onPlay={handlePlay}
            onToggleFavourite={handleToggleFavourite}
            onAddToPlaylist={setModalTrack}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === 'library' && (
          <LibraryView
            tracks={tracks}
            genres={genres}
            artists={artists}
            filters={filters}
            onFilterChange={setFilters}
            onPlay={handlePlay}
            onToggleFavourite={handleToggleFavourite}
            onAddToPlaylist={setModalTrack}
          />
        )}

        {activeTab === 'recommendations' && (
          <RecommendationsView
            recommendations={recommendations}
            meta={recMeta}
            mode={recMode}
            alpha={recAlpha}
            excludeRecent={excludeRecent}
            onChangeMode={setRecMode}
            onChangeAlpha={setRecAlpha}
            onToggleExcludeRecent={setExcludeRecent}
            onRefresh={() => loadRecommendations()}
            onPlay={handlePlay}
            onToggleFavourite={handleToggleFavourite}
            onAddToPlaylist={setModalTrack}
          />
        )}

        {activeTab === 'favourites' && (
          <LibraryView
            tracks={favourites}
            genres={genres}
            artists={artists}
            filters={filters}
            onPlay={handlePlay}
            onToggleFavourite={handleToggleFavourite}
            onAddToPlaylist={setModalTrack}
            title="Favourite Songs"
            subtitle="Tracks you have liked — strongly weighted in your AI taste profile."
          />
        )}

        {activeTab === 'playlists' && (
          <PlaylistsView
            playlists={playlists}
            onCreatePlaylist={handleCreatePlaylist}
            onDeletePlaylist={handleDeletePlaylist}
            onRemoveTrack={handleRemoveTrackFromPlaylist}
            onPlay={handlePlay}
          />
        )}

        {activeTab === 'history' && (
          <HistoryView history={history} onPlay={handlePlay} />
        )}

        {activeTab === 'profile' && (
          <ProfileView
            user={user}
            preferences={preferences}
            genres={genres}
            onSaveProfile={handleSaveProfile}
          />
        )}
      </main>

      <PlaylistModal
        track={modalTrack}
        playlists={playlists}
        onClose={() => setModalTrack(null)}
        onSelectPlaylist={handleAddTrackToPlaylist}
        onCreatePlaylist={handleCreatePlaylist}
      />

      <PlayerBar
        currentTrack={currentTrack}
        onToggleFavourite={handleToggleFavourite}
        onNext={() => {
          const pool = recommendations.length ? recommendations : tracks;
          if (!pool.length) return;
          const idx = pool.findIndex((t) => t.id === currentTrack?.id);
          handlePlay(pool[(idx + 1) % pool.length]);
        }}
      />

      <div aria-live="polite" className={toast ? 'toast' : 'visually-hidden'}>
        {toast}
      </div>
    </div>
  );
}
