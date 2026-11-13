import mockData from './mock.json';

const API_BASE_URL = (import.meta.env?.VITE_API_BASE_URL || '').trim().replace(/\/$/, '');
const OFFLINE_TOAST_MESSAGE = 'Backend offline: connect backend to simulate';

export function isMockMode() {
  return !API_BASE_URL;
}

export async function getVillages() {
  if (!API_BASE_URL) {
    return mockData.villages;
  }

  const response = await fetch(`${API_BASE_URL}/villages`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Failed to load villages (${response.status})`);
  }
  return response.json();
}

export async function getAlerts() {
  if (!API_BASE_URL) {
    return mockData.alerts;
  }

  const response = await fetch(`${API_BASE_URL}/alerts`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Failed to load alerts (${response.status})`);
  }
  return response.json();
}

export async function simulate(village_id, rainfall_mm) {
  if (!API_BASE_URL) {
    return {
      ok: false,
      offline: true,
      message: OFFLINE_TOAST_MESSAGE,
    };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ village_id, rainfall_mm }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      return {
        ok: false,
        offline: false,
        message: err.error || `Simulation failed (${response.status})`,
      };
    }

    const data = await response.json();
    return {
      ok: true,
      data,
    };
  } catch {
    return {
      ok: false,
      offline: true,
      message: OFFLINE_TOAST_MESSAGE,
    };
  }
}

export async function reset() {
  if (!API_BASE_URL) {
    return {
      ok: false,
      offline: true,
      message: OFFLINE_TOAST_MESSAGE,
    };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/reset`, {
      method: 'POST',
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      return {
        ok: false,
        offline: false,
        message: err.error || `Reset failed (${response.status})`,
      };
    }

    const data = await response.json();
    return {
      ok: true,
      data,
    };
  } catch {
    return {
      ok: false,
      offline: true,
      message: OFFLINE_TOAST_MESSAGE,
    };
  }
}
