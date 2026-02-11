import type { Metadata } from 'next';
import { ReactQueryProvider } from '@/lib/query-provider';
import { DashboardProvider } from '@/lib/contexts/dashboard-context';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'TrueCarbon - Carbon Credit MRV Dashboard',
  description: 'Measurement, Reporting, and Verification of Carbon Credits',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ReactQueryProvider>
          <DashboardProvider>
            {children}
          </DashboardProvider>
        </ReactQueryProvider>
      </body>
    </html>
  );
}
