/**
 * Error Boundary Component
 */

'use client';

import React, { ReactNode, ReactElement } from 'react';
import { ErrorMessage } from '@/components/ui/error-message';

interface Props {
  children: ReactNode;
  fallback?: ReactElement;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to monitoring service
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-4">
            <ErrorMessage
              title="Component Error"
              message={this.state.error?.message || 'An unexpected error occurred'}
              onRetry={() => this.setState({ hasError: false })}
            />
          </div>
        )
      );
    }

    return this.props.children;
  }
}
