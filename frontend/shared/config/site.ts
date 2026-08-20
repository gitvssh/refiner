export const SITE_NAME = "Refiner";
export const SITE_DESCRIPTION =
  "A privacy-first resume refinement workflow with an offline, deterministic demo.";
export const SITE_ORIGIN =
  process.env.NEXT_PUBLIC_SITE_ORIGIN ?? "http://localhost:3000";
export const API_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const CANONICAL_HOSTNAME = new URL(SITE_ORIGIN).hostname;
export const IS_INDEXABLE_ORIGIN =
  new URL(SITE_ORIGIN).protocol === "https:" &&
  CANONICAL_HOSTNAME !== "localhost";

export function isCanonicalHostname(hostname: string): boolean {
  return (
    IS_INDEXABLE_ORIGIN &&
    hostname.toLowerCase() === CANONICAL_HOSTNAME.toLowerCase()
  );
}

export function absoluteSiteUrl(path: string): string {
  return new URL(path, SITE_ORIGIN).toString();
}
