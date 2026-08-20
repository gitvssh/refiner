import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy",
  description:
    "The data-handling boundary of the Refiner reference application.",
  alternates: { canonical: "/privacy" },
};

export default function PrivacyPage() {
  return (
    <main className="legal-page">
      <p className="kicker">DATA BOUNDARY</p>
      <h1>Privacy is a property of the design.</h1>
      <div className="legal-grid">
        <section>
          <h2>Uploaded resume</h2>
          <p>
            Decoded in process memory for one request. The original bytes are
            never written to disk.
          </p>
        </section>
        <section>
          <h2>Derived draft</h2>
          <p>
            Held in one process for at most 15 minutes. It is removed
            immediately when the hashed, single-use export grant is consumed.
          </p>
        </section>
        <section>
          <h2>Analytics</h2>
          <p>
            Only aggregate, typed events may reach Cloudflare Zaraz after
            consent. Document text, filenames, names, contact details, and URLs
            are rejected by the transport boundary.
          </p>
        </section>
        <section>
          <h2>External AI</h2>
          <p>
            Disabled in this public edition. The deterministic adapter makes the
            full flow auditable without transmitting content or configuring
            credentials.
          </p>
        </section>
      </div>
    </main>
  );
}
