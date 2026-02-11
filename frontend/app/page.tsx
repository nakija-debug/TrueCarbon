'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-emerald-50" style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom right, #eff6ff, #f0fdf4)'
    }}>
      <div className="mx-auto max-w-7xl px-4 py-20 text-center" style={{
        maxWidth: '80rem',
        margin: '0 auto',
        padding: '5rem 1rem',
        textAlign: 'center'
      }}>
        <h1 className="mb-6 text-5xl font-bold text-gray-900" style={{
          marginBottom: '1.5rem',
          fontSize: '3rem',
          fontWeight: 'bold',
          color: '#111827'
        }}>
          TrueCarbon
        </h1>
        <p className="mb-8 text-xl text-gray-600" style={{
          marginBottom: '2rem',
          fontSize: '1.25rem',
          color: '#4b5563'
        }}>
          Carbon Credit Measurement, Reporting, and Verification Platform
        </p>
        
        <Link
          href="/dashboard"
          className="inline-block rounded-lg bg-emerald-600 px-8 py-4 text-lg font-semibold text-white hover:bg-emerald-700 transition-colors"
          style={{
            display: 'inline-block',
            borderRadius: '0.5rem',
            backgroundColor: '#16a34a',
            padding: '1rem 2rem',
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#ffffff',
            textDecoration: 'none',
            transition: 'background-color 0.3s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#15803d'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#16a34a'}
        >
          Go to Dashboard
        </Link>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8" style={{
          marginTop: '5rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '2rem'
        }}>
          <div className="rounded-lg bg-white p-8 shadow" style={{
            borderRadius: '0.5rem',
            backgroundColor: '#ffffff',
            padding: '2rem',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div className="mb-4 text-4xl" style={{ marginBottom: '1rem', fontSize: '2.25rem' }}>🌍</div>
            <h3 className="mb-2 text-lg font-semibold" style={{
              marginBottom: '0.5rem',
              fontSize: '1.125rem',
              fontWeight: '600'
            }}>Geospatial Analysis</h3>
            <p className="text-gray-600" style={{ color: '#4b5563' }}>Sentinel-2 NDVI and Dynamic World LULC integration</p>
          </div>

          <div className="rounded-lg bg-white p-8 shadow" style={{
            borderRadius: '0.5rem',
            backgroundColor: '#ffffff',
            padding: '2rem',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div className="mb-4 text-4xl" style={{ marginBottom: '1rem', fontSize: '2.25rem' }}>📊</div>
            <h3 className="mb-2 text-lg font-semibold" style={{
              marginBottom: '0.5rem',
              fontSize: '1.125rem',
              fontWeight: '600'
            }}>Carbon Quantification</h3>
            <p className="text-gray-600" style={{ color: '#4b5563' }}>IPCC Tier 2 methodology with Monte Carlo analysis</p>
          </div>

          <div className="rounded-lg bg-white p-8 shadow" style={{
            borderRadius: '0.5rem',
            backgroundColor: '#ffffff',
            padding: '2rem',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div className="mb-4 text-4xl" style={{ marginBottom: '1rem', fontSize: '2.25rem' }}>✅</div>
            <h3 className="mb-2 text-lg font-semibold" style={{
              marginBottom: '0.5rem',
              fontSize: '1.125rem',
              fontWeight: '600'
            }}>Verification</h3>
            <p className="text-gray-600" style={{ color: '#4b5563' }}>Comprehensive compliance and audit reporting</p>
          </div>
        </div>
      </div>
    </main>
  );
}
