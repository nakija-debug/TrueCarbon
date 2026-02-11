/**
 * Skeleton Loading Components
 */

import React from 'react';

export function CardSkeleton({ count = 1 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="h-6 w-32 animate-pulse rounded bg-gray-200"></div>
          <div className="mt-4 h-4 w-full animate-pulse rounded bg-gray-200"></div>
          <div className="mt-2 h-4 w-3/4 animate-pulse rounded bg-gray-200"></div>
        </div>
      ))}
    </>
  );
}

export function ChartSkeleton() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <div className="h-6 w-32 animate-pulse rounded bg-gray-200"></div>
      <div className="mt-6 h-64 animate-pulse rounded bg-gray-100"></div>
    </div>
  );
}

export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <div className="space-y-4">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4">
            {Array.from({ length: columns }).map((_, j) => (
              <div key={j} className="h-4 flex-1 animate-pulse rounded bg-gray-200"></div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function MapSkeleton() {
  return (
    <div className="h-96 w-full animate-pulse rounded-lg bg-gray-200"></div>
  );
}
