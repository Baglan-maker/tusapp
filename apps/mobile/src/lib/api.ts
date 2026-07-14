/**
 * Typed client for the FastAPI backend.
 *
 * Every call carries the Supabase JWT — the API takes the user id from the
 * token, never from a parameter. A 402 means the free daily quota is spent and
 * the caller should route to the paywall.
 */

import { supabase } from './supabase';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export type Lens = 'psych' | 'classic' | 'ibn_sirin' | 'science';
export type AppLocale = 'ru' | 'kk';

export class QuotaError extends Error {
  constructor() {
    super('quota');
    this.name = 'QuotaError';
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function authHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { ...(init.headers ?? {}), ...(await authHeader()) },
    });
  } catch {
    // Offline / DNS / server down — surfaced as a retry banner, never swallowed.
    throw new ApiError('network', 0);
  }

  if (response.status === 402) throw new QuotaError();
  if (!response.ok) {
    throw new ApiError(await response.text().catch(() => 'error'), response.status);
  }
  return (await response.json()) as T;
}

// ---------------------------------------------------------------- profile

export type Profile = {
  locale: AppLocale;
  default_lens: Lens;
  /** null == "по-разному" */
  wake_time: string | null;
  timezone: string;
  push_enabled: boolean;
  onboarding_completed: boolean;
};

export function getProfile(): Promise<Profile> {
  return request<Profile>('/profile');
}

export function updateProfile(patch: Partial<Profile>): Promise<Profile> {
  return request<Profile>('/profile', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  });
}

// ---------------------------------------------------------------- dreams

export type DreamCreated = {
  dream_id: string;
  transcript: string | null;
  language: string | null;
};

export type Interpretation = {
  id: string;
  dream_id: string;
  lens: Lens;
  model: string;
  content_md: string;
  tokens_in: number | null;
  tokens_out: number | null;
  created_at: string;
};

export function createDreamFromAudio(params: {
  uri: string;
  language: AppLocale;
  emotionsInDream: string[];
  emotionsOnWaking: string[];
}): Promise<DreamCreated> {
  const form = new FormData();
  form.append('language', params.language);
  form.append('emotions_in_dream', params.emotionsInDream.join(','));
  form.append('emotions_on_waking', params.emotionsOnWaking.join(','));
  form.append('audio', {
    uri: params.uri,
    name: 'dream.m4a',
    type: 'audio/m4a',
  } as unknown as Blob);
  return request<DreamCreated>('/dreams', { method: 'POST', body: form });
}

export function createDreamFromText(params: {
  text: string;
  language: AppLocale;
  emotionsInDream: string[];
  emotionsOnWaking: string[];
}): Promise<DreamCreated> {
  const form = new FormData();
  form.append('language', params.language);
  form.append('text', params.text);
  form.append('emotions_in_dream', params.emotionsInDream.join(','));
  form.append('emotions_on_waking', params.emotionsOnWaking.join(','));
  return request<DreamCreated>('/dreams', { method: 'POST', body: form });
}

export function updateTranscript(dreamId: string, transcript: string): Promise<unknown> {
  return request(`/dreams/${dreamId}/transcript`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript }),
  });
}

export function interpretDream(dreamId: string, lens: Lens): Promise<Interpretation> {
  return request<Interpretation>(`/dreams/${dreamId}/interpret?lens=${lens}`, {
    method: 'POST',
  });
}
