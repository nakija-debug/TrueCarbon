/**
 * API utility functions for Next.js API routes
 */

import { NextRequest, NextResponse } from 'next/server';
import axiosInstance from '@/lib/api-client';

/**
 * Proxy request to FastAPI backend
 */
export async function proxyToFastAPI(
  method: string,
  endpoint: string,
  data?: unknown,
  headers?: Record<string, string>
) {
  const url = `${(process.env as any).NEXT_PUBLIC_API_URL}${endpoint}`;

  try {
    const response = await axiosInstance({
      method,
      url,
      data,
      headers,
    });
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Proxy error: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Extract auth headers from request
 */
export function getAuthHeaders(request: NextRequest): Record<string, string> {
  const headers: Record<string, string> = {};
  const authHeader = request.headers.get('authorization');
  if (authHeader) {
    headers['Authorization'] = authHeader;
  }
  return headers;
}

/**
 * Handle API errors in Next.js API routes
 */
export function handleApiError(error: unknown) {
  console.error('API Error:', error);

  if (error instanceof Error) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }

  return NextResponse.json(
    { error: 'Internal server error' },
    { status: 500 }
  );
}

/**
 * Validate request against schema (basic implementation)
 */
export function validateRequest<T>(data: unknown, requiredFields: (keyof T)[]): data is T {
  if (!data || typeof data !== 'object') {
    return false;
  }

  const obj = data as Record<string, unknown>;
  return requiredFields.every((field) => field in obj);
}
