import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import {
  SITE_DESCRIPTION,
  SITE_NAME,
  SITE_ORIGIN,
  absoluteSiteUrl,
} from "@/shared/config/site";

import "./styles.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_ORIGIN),
  title: {
    default: `${SITE_NAME} · Private resume workflow`,
    template: `%s · ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  icons: { icon: "/icon.svg" },
  alternates: { canonical: "/" },
  openGraph: {
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    type: "website",
    url: "/",
  },
  twitter: {
    card: "summary",
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
  },
};

const structuredData = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      name: SITE_NAME,
      url: SITE_ORIGIN,
    },
    {
      "@type": "WebApplication",
      name: SITE_NAME,
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      url: SITE_ORIGIN,
      description: SITE_DESCRIPTION,
      privacyPolicy: absoluteSiteUrl("/privacy"),
    },
  ],
}).replace(/</g, "\\u003c");

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <Link className="brand" href="/">
            <span>R/</span> Refiner
          </Link>
          <nav aria-label="Primary navigation">
            <a href="https://github.com/gitvssh/refiner">Source</a>
            <Link href="/privacy">Privacy</Link>
          </nav>
        </header>
        {children}
        <footer>
          <span>Built as a transparent reference workflow.</span>
          <span>Uploads are not retained.</span>
        </footer>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: structuredData }}
        />
      </body>
    </html>
  );
}
