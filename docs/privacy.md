# Privacy design

## Data lifecycle

| Data | Location | Maximum lifetime | Removal |
| --- | --- | --- | --- |
| Uploaded bytes | Request memory | One request | Released after decoding |
| Job description | Request/workflow memory | One request | Released with workflow state |
| Derived draft | In-process grant store | 15 minutes | Atomic token consume or TTL cleanup |
| Export token | Client only; SHA-256 digest in store | 15 minutes | Atomic token consume or TTL cleanup |
| PDF | Response body | One response | Client controls downloaded copy |

No request field is included in application logs or analytics properties. The public edition has no
database and no external AI adapter.

## Threat-oriented choices

- A token digest does not reveal the bearer token if process diagnostics are exposed.
- Generic not-found responses do not distinguish expired, consumed, and unknown tokens.
- The store removes a record before rendering, so parallel requests cannot export twice.
- Upload size, text encoding, and length limits bound memory and parser behavior.
- The reference Compose service uses a read-only filesystem and a small temporary filesystem.

The application is still a reference, not a hardened multi-tenant service. Authentication,
distributed rate limiting, encrypted durable storage, data-subject requests, and provider-specific
privacy terms require a separate design review.
