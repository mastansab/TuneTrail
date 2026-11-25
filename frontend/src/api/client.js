const API_BASE = '/api';

export function getToken() {
  return localStorage.getItem('tunetrail_token');
}

export function setToken(token) {
  if (token) {
    localStorage.setItem('tunetrail_token', token);
  } else {
    localStorage.removeItem('tunetrail_token');
  }
}

export async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}
