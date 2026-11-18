// 404 for URLs outside every root layout (unknown country, unserved language, unknown path).
// The app has several root layouts (/{country}/{lang} and /staff), so it needs its own <html>.
import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { fontVars } from "./fonts";

export const metadata: Metadata = { title: "Page not found", robots: { index: false } };

export default function GlobalNotFound() {
  return (
    <html lang="en" className={fontVars}>
      <body className="min-h-screen">
        <main className="mx-auto max-w-xl p-8">
          <h1 className="text-2xl font-semibold">Page not found</h1>
          <p className="mt-2">
            <Link href="/" className="text-blue-800 underline">
              Go to Explore
            </Link>
          </p>
        </main>
      </body>
    </html>
  );
}
