import Link from "next/link";

// Shown for notFound() inside a country × language page (unknown model, list or term).
export default function NotFound() {
  return (
    <div className="max-w-xl py-8">
      <h1 className="text-2xl font-semibold">Page not found</h1>
      <p className="mt-2">
        <Link href="/" className="text-blue-800 underline">
          Go to Explore
        </Link>
      </p>
    </div>
  );
}
