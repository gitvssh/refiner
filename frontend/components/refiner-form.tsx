"use client";

import { FormEvent, useMemo, useState } from "react";

import { consumePdfExport, createRefinement, Refinement } from "@/shared/api";
import { trackEvent } from "@/shared/analytics/transport";

function coverageBand(score: number): "low" | "medium" | "high" {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
}

export function RefinerForm() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<Refinement | null>(null);
  const [exportAvailable, setExportAvailable] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  const canSubmit = useMemo(
    () => Boolean(file && jobDescription.trim().length >= 40 && !busy),
    [file, jobDescription, busy],
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || !canSubmit) return;
    setBusy(true);
    setMessage("");
    setResult(null);
    setExportAvailable(false);
    trackEvent("refinement_started", { source: "upload" });
    try {
      const refinement = await createRefinement(file, jobDescription);
      setResult(refinement);
      setExportAvailable(true);
      trackEvent("refinement_completed", {
        coverageBand: coverageBand(refinement.analysis.coverage_score),
      });
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "The request could not be completed.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function downloadPdf() {
    if (!result || !exportAvailable) return;
    setBusy(true);
    setMessage("");
    try {
      const pdf = await consumePdfExport(result.export_token);
      const href = URL.createObjectURL(pdf);
      const anchor = document.createElement("a");
      anchor.href = href;
      anchor.download = "refined-resume.pdf";
      anchor.click();
      URL.revokeObjectURL(href);
      setExportAvailable(false);
      setMessage(
        "PDF downloaded. The single-use export grant has been consumed.",
      );
      trackEvent("pdf_exported", { format: "pdf" });
    } catch (error) {
      setExportAvailable(false);
      setMessage(
        error instanceof Error
          ? error.message
          : "The PDF could not be downloaded.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="workspace">
      <form className="panel input-panel" onSubmit={submit}>
        <div className="eyebrow">01 · PRIVATE INPUT</div>
        <h2>Bring the evidence, not the noise.</h2>
        <p className="muted">
          Upload UTF-8 text only. Bytes are processed in memory and never
          written to disk.
        </p>
        <label className="field">
          <span>Resume (.txt or .md)</span>
          <input
            type="file"
            accept=".txt,.md,text/plain,text/markdown"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            required
          />
        </label>
        <label className="field">
          <span>Job description</span>
          <textarea
            rows={12}
            minLength={40}
            maxLength={20000}
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
            placeholder="Paste a synthetic or public job description here…"
            required
          />
        </label>
        <button className="primary" type="submit" disabled={!canSubmit}>
          {busy ? "Refining…" : "Run private refinement"}
        </button>
        <small>No account · no external model · no durable upload</small>
      </form>

      <section className="panel result-panel" aria-live="polite">
        <div className="eyebrow">02 · REVIEWABLE OUTPUT</div>
        {!result ? (
          <div className="empty-state">
            <span>R</span>
            <h2>Your evidence map appears here.</h2>
            <p>
              Use the synthetic fixtures from the repository for a deterministic
              demonstration.
            </p>
          </div>
        ) : (
          <>
            <div className="score-row">
              <div>
                <span className="score">{result.analysis.coverage_score}</span>
                <span className="score-unit">%</span>
              </div>
              <p>keyword coverage before human review</p>
            </div>
            <div className="insight-grid">
              <article>
                <h3>Matched</h3>
                <p>
                  {result.analysis.matched_keywords.join(" · ") ||
                    "No direct matches yet"}
                </p>
              </article>
              <article>
                <h3>Review gaps</h3>
                <p>
                  {result.analysis.missing_keywords.join(" · ") ||
                    "No major keyword gaps"}
                </p>
              </article>
            </div>
            <div className="draft">
              <h3>Role-focused draft</h3>
              <pre>{result.rewritten_resume}</pre>
            </div>
            <button
              className="secondary"
              type="button"
              onClick={downloadPdf}
              disabled={busy || !exportAvailable}
            >
              {exportAvailable
                ? "Download one-time PDF"
                : "Export grant consumed"}
            </button>
          </>
        )}
        {message && <p className="message">{message}</p>}
      </section>
    </div>
  );
}
