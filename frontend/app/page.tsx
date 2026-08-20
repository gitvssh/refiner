import { RefinerForm } from "@/components/refiner-form";

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <p className="kicker">PRIVACY-FIRST · DETERMINISTIC · REVIEWABLE</p>
          <h1>
            Make the fit visible.
            <br />
            Keep the resume private.
          </h1>
          <p className="lede">
            A reference workflow that separates domain evidence, orchestration,
            storage, and export so every privacy claim can be inspected in code.
          </p>
        </div>
        <div className="hero-proof" aria-label="Product guarantees">
          <div>
            <strong>0</strong>
            <span>external model calls</span>
          </div>
          <div>
            <strong>15m</strong>
            <span>maximum derived-draft TTL</span>
          </div>
          <div>
            <strong>1×</strong>
            <span>export token use</span>
          </div>
        </div>
      </section>
      <RefinerForm />
    </main>
  );
}
