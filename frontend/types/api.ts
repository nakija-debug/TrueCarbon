/**
 * Common API types
 */

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  status: number;
  detail: string;
  message?: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface DateRangeFilter {
  startDate: string; // YYYY-MM-DD format
  endDate: string; // YYYY-MM-DD format
}

export interface ApiErrorResponse {
  detail: string;
  status?: number;
}
