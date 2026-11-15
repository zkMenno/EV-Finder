import type { MetadataRoute } from "next";
import { getCatalogue } from "@/lib/catalogue";
import { sitemapUrls } from "@/lib/sitemap";
import { siteUrl } from "@/lib/site-paths";

export default function sitemap(): MetadataRoute.Sitemap {
  const cat = getCatalogue();
  const lastModified = cat.generatedAt();
  return sitemapUrls(cat, siteUrl()).map((url) => ({ url, lastModified }));
}
