// Root layout for staff pages (EN only, never indexed, never linked). Separate from the public
// /{country}/{lang} root layout (Decision 015). Checks the staff credentials itself (A-05 F2):
// the proxy's 401 challenge is a convenience, not the only lock.
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { requireStaff } from "@/lib/staff-guard";
import "../globals.css";
import { fontVars } from "../fonts";

export const dynamic = "force-dynamic";

export const metadata: Metadata = { robots: { index: false, follow: false } };

export default async function StaffLayout({ children }: { children: ReactNode }) {
  await requireStaff();
  return (
    <html lang="en" className={fontVars}>
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
