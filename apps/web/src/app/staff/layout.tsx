// Root layout for staff pages (EN only, never indexed, never linked). Separate from the public
// /{country}/{lang} root layout (Decision 015).
import type { Metadata } from "next";
import type { ReactNode } from "react";
import "../globals.css";

export const metadata: Metadata = { robots: { index: false, follow: false } };

export default function StaffLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
