import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { siteName } from "@/config/site";
import { requestLang } from "@/lib/request-lang";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: siteName, template: `%s · ${siteName}` },
  description: "Independent finder for new and used electric cars: real-world range, charging and prices.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default async function RootLayout({ children }: { children: ReactNode }) {
  const lang = await requestLang();
  return (
    <html lang={lang}>
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
