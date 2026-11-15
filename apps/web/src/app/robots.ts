import type { MetadataRoute } from "next";
import { siteUrl } from "@/lib/site-paths";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{ userAgent: "*", allow: "/", disallow: ["/staff/", "/*/*/compare"] }],
    sitemap: `${siteUrl()}/sitemap.xml`,
  };
}
