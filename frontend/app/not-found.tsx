import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 text-center">
            <h2 className="mb-4 text-3xl font-bold text-gray-900">404 - Page Not Found</h2>
            <p className="mb-8 text-gray-600">Could not find the requested resource</p>
            <Link
                href="/"
                className="rounded-lg bg-green-600 px-6 py-3 text-white transition-colors hover:bg-green-700"
            >
                Return Home
            </Link>
        </div>
    );
}
