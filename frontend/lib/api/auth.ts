/**
 * Auth API Module
 * Handles authentication requests to FastAPI backend
 */

import axiosInstance from '../api-client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await axiosInstance.post<LoginResponse>('/api/v1/auth', {
    ...credentials,
    action: 'login',
  });
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
  }
  return response.data;
}

/**
 * Register new user
 */
export async function register(data: RegisterRequest) {
  const response = await axiosInstance.post('/api/v1/auth', {
    ...data,
    action: 'register',
  });
  return response.data;
}

/**
 * Refresh access token
 */
export async function refreshToken(token: string): Promise<LoginResponse> {
  const response = await axiosInstance.post<LoginResponse>('/api/v1/auth', {
    refresh_token: token,
    action: 'refresh',
  });
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
  }
  return response.data;
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    await axiosInstance.post('/api/v1/auth', { action: 'logout' });
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

/**
 * Get current stored token
 */
export function getStoredToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}

/**
 * Clear stored tokens
 */
export function clearTokens(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
