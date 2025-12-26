// js/api.js — работа с backend + localStorage
// Модульная версия с ES6 export

const API_BASE = "";
const LS_KEYS = {
  requests: "rr_requests_v1",
  auth: "rr_auth_v1",
};

// ========== LOCALSTORAGE (REQUESTS) ==========

export function saveRequestsToStorage(requests) {
  localStorage.setItem(LS_KEYS.requests, JSON.stringify(requests));
}

export function loadRequestsFromStorage() {
  const raw = localStorage.getItem(LS_KEYS.requests);
  if (!raw) return [];
  try {
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

// ========== LOCALSTORAGE (AUTH) ==========

export function saveAuthToStorage(user) {
  localStorage.setItem(LS_KEYS.auth, JSON.stringify({ user }));
}

export function loadAuthFromStorage() {
  const raw = localStorage.getItem(LS_KEYS.auth);
  if (!raw) return null;
  try {
    const obj = JSON.parse(raw);
    return obj?.user ?? null;
  } catch {
    return null;
  }
}

export function clearAuthStorage() {
  localStorage.removeItem(LS_KEYS.auth);
}

export function getAuthToken() {
  const u = loadAuthFromStorage();
  return u?.token || "";
}

// ========== FETCH WRAPPER ==========

export async function apiFetch(path, options = {}) {
  const base = API_BASE || "";
  const url = base.replace(/\/+$/, "") + "/" + path.replace(/^\/+/, "");
  const token = getAuthToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, {
    ...options,
    headers,
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const err = (data && data.error) || `HTTP_${res.status}`;
    throw new Error(err);
  }

  return data;
}

// ========== AUTH ==========

export async function apiLogin(login, password) {
  const data = await apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ login, password }),
  });

  const user = {
    id: data.user_id,
    login: data.login,
    name: data.full_name,
    full_name: data.full_name,
    role: data.user_type,
    user_type: data.user_type,
    token: data.access_token,
  };

  saveAuthToStorage(user);
  return user;
}

// ========== USERS ==========

export async function apiFetchSpecialists() {
  const res = await apiFetch("/api/users/specialists", { method: "GET" });
  return res?.data || res || [];
}

export async function apiFetchAllUsers() {
  const res = await apiFetch("/api/users", { method: "GET" });
  return res?.data || res || [];
}

// ========== REQUESTS ==========

export async function apiFetchRequests() {
  return apiFetch("/api/requests/");
}

export async function apiCreateRequest(payload) {
  return apiFetch("/api/requests/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function apiUpdateRequest(id, payload) {
  return apiFetch(`/api/requests/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
// REQUESTS
export async function apiDeleteRequest(id) {
  return apiFetch(`api/requests/${id}`, { method: 'DELETE' });
}
