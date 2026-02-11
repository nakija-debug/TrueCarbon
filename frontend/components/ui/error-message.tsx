/**
 * Error Message Component
 */

import React from 'react';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({
  title = 'Error',
  message,
  onRetry,
  className = '',
}: ErrorMessageProps) {
  return (
    <div
      className={`rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 ${className}`}
      role="alert"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p className="mt-1 text-sm">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-4 rounded bg-red-200 px-3 py-2 text-sm font-medium text-red-800 hover:bg-red-300"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
