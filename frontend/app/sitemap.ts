import type { MetadataRoute } from "next";

import { absoluteSiteUrl } from "@/shared/config/site";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: absoluteSiteUrl("/"), changeFrequency: "monthly", priority: 1 },
    {
      url: absoluteSiteUrl("/privacy"),
      changeFrequency: "yearly",
      priority: 0.5,
    },
  ];
}
