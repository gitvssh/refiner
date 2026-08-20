import { describe, expect, it } from "vitest";

import { propertiesAreSafe, trackEvent } from "./transport";

describe("analytics privacy boundary", () => {
  it("accepts the documented aggregate properties", () => {
    expect(propertiesAreSafe({ coverageBand: "high" })).toBe(true);
  });

  it("rejects properties that could carry personal document data", () => {
    expect(propertiesAreSafe({ filename: "synthetic.txt" })).toBe(false);
    expect(propertiesAreSafe({ resumeText: "not allowed" })).toBe(false);
  });

  it("does not throw when Zaraz is unavailable", () => {
    expect(trackEvent("pdf_exported", { format: "pdf" })).toBe(false);
  });
});
