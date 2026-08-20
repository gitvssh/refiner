import type { MetadataRoute } from "next";

import { IS_INDEXABLE_ORIGIN, SITE_ORIGIN } from "@/shared/config/site";

export default function robots(): MetadataRoute.Robots {
  if (!IS_INDEXABLE_ORIGIN) {
    return { rules: [{ userAgent: "*", disallow: "/" }] };
  }
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/api/", "/health"],
      },
    ],
    sitemap: `${SITE_ORIGIN}/sitemap.xml`,
  };
}
