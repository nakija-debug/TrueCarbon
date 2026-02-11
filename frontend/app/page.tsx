import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-emerald-50">
      <div className="mx-auto max-w-7xl px-4 py-20 text-center">
        <h1 className="mb-6 text-5xl font-bold text-gray-900">
          TrueCarbon
        </h1>
        <p className="mb-8 text-xl text-gray-600">
          Carbon Credit Measurement, Reporting, and Verification Platform
        </p>
        
        <Link
          href="/dashboard"
          className="inline-block rounded-lg bg-emerald-600 px-8 py-4 text-lg font-semibold text-white hover:bg-emerald-700 transition-colors"
        >
          Go to Dashboard
        </Link>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="rounded-lg bg-white p-8 shadow">
            <div className="mb-4 text-4xl">🌍</div>
            <h3 className="mb-2 text-lg font-semibold">Geospatial Analysis</h3>
            <p className="text-gray-600">Sentinel-2 NDVI and Dynamic World LULC integration</p>
          </div>

          <div className="rounded-lg bg-white p-8 shadow">
            <div className="mb-4 text-4xl">📊</div>
            <h3 className="mb-2 text-lg font-semibold">Carbon Quantification</h3>
            <p className="text-gray-600">IPCC Tier 2 methodology with Monte Carlo analysis</p>
          </div>

          <div className="rounded-lg bg-white p-8 shadow">
            <div className="mb-4 text-4xl">✅</div>
            <h3 className="mb-2 text-lg font-semibold">Verification</h3>
            <p className="text-gray-600">Comprehensive compliance and audit reporting</p>
          </div>
        </div>
      </div>
    </main>
  );
}
