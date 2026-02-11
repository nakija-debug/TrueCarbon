'use client';

import React from 'react';
import { CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface VerificationPanelProps {}

interface VerificationItem {
  id: string;
  name: string;
  status: 'verified' | 'pending' | 'failed';
  timestamp?: string;
  auditor?: string;
}

const VerificationPanel: React.FC<VerificationPanelProps> = () => {
  const [verifications] = React.useState<VerificationItem[]>([
    {
      id: '1',
      name: 'NDVI Data Validation',
      status: 'verified',
      timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      auditor: 'Auditor A',
    },
    {
      id: '2',
      name: 'Carbon Methodology Audit',
      status: 'pending',
      auditor: 'Auditor B',
    },
    {
      id: '3',
      name: 'Field Survey Verification',
      status: 'verified',
      timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      auditor: 'Auditor C',
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'bg-emerald-50 border-emerald-200';
      case 'pending':
        return 'bg-yellow-50 border-yellow-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return (
          <CheckCircleIcon className="h-5 w-5 text-emerald-600" />
        );
      case 'pending':
        return (
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
        );
      case 'failed':
        return (
          <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
        );
      default:
        return null;
    }
  };

  const verifiedCount = verifications.filter(
    (v) => v.status === 'verified'
  ).length;

  return (
    <div className="rounded-xl bg-white p-6 shadow-lg">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">
          Verification Status
        </h2>
        <div className="text-sm font-medium text-gray-600">
          {verifiedCount}/{verifications.length} Verified
        </div>
      </div>

      <div className="space-y-4">
        {verifications.map((item) => (
          <div
            key={item.id}
            className={`rounded-lg border p-4 ${getStatusColor(item.status)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                {getStatusIcon(item.status)}
                <div>
                  <h3 className="font-semibold text-gray-900">{item.name}</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    {item.status === 'verified' && 'Verified by '}{item.auditor}
                  </p>
                  {item.timestamp && (
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
              <span
                className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${
                  item.status === 'verified'
                    ? 'bg-emerald-100 text-emerald-800'
                    : item.status === 'pending'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                }`}
              >
                {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 border-t border-gray-200 pt-6">
        <div className="rounded-lg bg-blue-50 p-4">
          <h4 className="mb-2 font-semibold text-blue-900">
            Verification Process
          </h4>
          <ol className="space-y-2 text-sm text-blue-800">
            <li>1. Data Collection & Validation</li>
            <li>2. Methodology Review</li>
            <li>3. Field Survey & Audit</li>
            <li>4. Blockchain Registration</li>
            <li>5. Credit Issuance</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default VerificationPanel;
