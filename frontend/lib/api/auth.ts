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

/**
 * Login user and get tokens
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await axiosInstance.post<LoginResponse>('/auth/login', credentials);
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
  const response = await axiosInstance.post('/auth/register', data);
  return response.data;
}

/**
 * Refresh access token
 */
export async function refreshToken(token: string): Promise<LoginResponse> {
  const response = await axiosInstance.post<LoginResponse>('/auth/refresh', {
    refresh_token: token,
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
    await axiosInstance.post('/auth/logout', {});
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
