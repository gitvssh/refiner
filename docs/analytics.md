# Consent-gated analytics contract

The browser adapter calls `window.zaraz.track` only when Cloudflare Zaraz is present. Application
code contains no GA4 measurement ID. Zaraz Consent must default analytics to denied and enable it
only after a visitor grants consent.

| Event | Allowed properties | Purpose | Suggested GA4 key event |
| --- | --- | --- | --- |
| `refinement_started` | `source`: `sample` or `upload` | Understand workflow starts | no |
| `refinement_completed` | `coverageBand`: `low`, `medium`, `high` | Observe successful completion | yes |
| `pdf_exported` | `format`: `pdf` | Observe delivery of user value | yes |

The typed transport rejects property names related to content, documents, files, names, resumes,
email addresses, phone numbers, text, and URLs. Filenames and document values must never be added to
the event dictionary.

Status: the application contract is implemented. A production deployment would still need a human
to connect Zaraz Consent, GA4, key events, and Search Console in their respective consoles.
