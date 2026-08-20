"use client";

type AnalyticsEvents = {
  refinement_started: { source: "sample" | "upload" };
  refinement_completed: { coverageBand: "low" | "medium" | "high" };
  pdf_exported: { format: "pdf" };
};

const FORBIDDEN_PROPERTY =
  /(content|document|email|file|name|phone|resume|text|url)/i;

declare global {
  interface Window {
    zaraz?: {
      track: (event: string, properties: Record<string, string>) => void;
    };
  }
}

export function propertiesAreSafe(properties: Record<string, string>): boolean {
  return Object.keys(properties).every((key) => !FORBIDDEN_PROPERTY.test(key));
}

export function trackEvent<EventName extends keyof AnalyticsEvents>(
  event: EventName,
  properties: AnalyticsEvents[EventName],
): boolean {
  const safeProperties = properties as Record<string, string>;
  if (
    !propertiesAreSafe(safeProperties) ||
    typeof window === "undefined" ||
    !window.zaraz
  ) {
    return false;
  }
  window.zaraz.track(event, safeProperties);
  return true;
}
