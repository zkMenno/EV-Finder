import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-xl p-8">
      <h1 className="text-2xl font-semibold">Page not found</h1>
      <p className="mt-2">
        <Link href="/nl" className="text-blue-800 underline">
          Go to Explore
        </Link>
      </p>
    </main>
  );
}
