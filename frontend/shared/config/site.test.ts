import { describe, expect, it } from "vitest";

import {
  CANONICAL_HOSTNAME,
  IS_INDEXABLE_ORIGIN,
  SITE_ORIGIN,
  absoluteSiteUrl,
  isCanonicalHostname,
} from "./site";

describe("site configuration", () => {
  it("uses one origin for absolute URLs", () => {
    expect(absoluteSiteUrl("/privacy")).toBe(
      new URL("/privacy", SITE_ORIGIN).toString(),
    );
  });

  it("keeps the local default out of search indexes", () => {
    if (CANONICAL_HOSTNAME === "localhost") {
      expect(IS_INDEXABLE_ORIGIN).toBe(false);
      expect(isCanonicalHostname("localhost")).toBe(false);
    }
  });
});
