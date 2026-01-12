/**
 * Auth Hook
 * Handles JWT token storage and refresh for the frontend.
 */

'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

interface TokenPayload {
  exp?: number;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

interface UseAuthReturn {
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<AuthTokens | null>;
  register: (email: string, password: string) => Promise<AuthTokens | null>;
  logout: () => void;
  getValidAccessToken: () => Promise<string | null>;
}

const STORAGE_KEY = 'arc-auth-tokens';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function decodeToken(token: string): TokenPayload | null {
  try {
    const [, payload] = token.split('.');
    if (!payload) return null;
    const decoded = JSON.parse(atob(payload));
    return decoded as TokenPayload;
  } catch {
    return null;
  }
}

function loadTokens(): AuthTokens | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AuthTokens) : null;
  } catch {
    return null;
  }
}

function storeTokens(tokens: AuthTokens | null) {
  if (typeof window === 'undefined') return;
  if (!tokens) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
}

function buildTokens(response: AuthResponse): AuthTokens {
  const expiresAt = Date.now() + response.expires_in * 1000;
  return {
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    expiresAt,
  };
}

function isExpired(tokens: AuthTokens | null): boolean {
  if (!tokens) return true;
  const payload = decodeToken(tokens.accessToken);
  if (payload?.exp) {
    return payload.exp * 1000 < Date.now();
  }
  return tokens.expiresAt < Date.now();
}

async function requestTokens(
  path: string,
  payload: Record<string, string>
): Promise<AuthTokens | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as AuthResponse;
    return buildTokens(data);
  } catch {
    return null;
  }
}

export function useAuth(): UseAuthReturn {
  const [tokens, setTokens] = useState<AuthTokens | null>(() => loadTokens());

  const isAuthenticated = useMemo(() => !isExpired(tokens), [tokens]);

  const persistTokens = useCallback((next: AuthTokens | null) => {
    setTokens(next);
    storeTokens(next);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const newTokens = await requestTokens('/auth/login', { email, password });
    if (newTokens) {
      persistTokens(newTokens);
    }
    return newTokens;
  }, [persistTokens]);

  const register = useCallback(async (email: string, password: string) => {
    const newTokens = await requestTokens('/auth/register', { email, password });
    if (newTokens) {
      persistTokens(newTokens);
    }
    return newTokens;
  }, [persistTokens]);

  const logout = useCallback(() => {
    persistTokens(null);
  }, [persistTokens]);

  const refreshTokens = useCallback(async () => {
    if (!tokens?.refreshToken) {
      persistTokens(null);
      return null;
    }
    const newTokens = await requestTokens('/auth/refresh', {
      refresh_token: tokens.refreshToken,
    });
    if (newTokens) {
      persistTokens(newTokens);
    }
    return newTokens;
  }, [persistTokens, tokens?.refreshToken]);

  const getValidAccessToken = useCallback(async () => {
    if (!tokens) return null;
    if (!isExpired(tokens)) return tokens.accessToken;
    const refreshed = await refreshTokens();
    return refreshed?.accessToken ?? null;
  }, [refreshTokens, tokens]);

  useEffect(() => {
    if (!tokens) return;
    if (isExpired(tokens)) {
      void refreshTokens();
    }
  }, [refreshTokens, tokens]);

  return {
    tokens,
    isAuthenticated,
    login,
    register,
    logout,
    getValidAccessToken,
  };
}

export default useAuth;
