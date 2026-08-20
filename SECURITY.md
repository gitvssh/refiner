# Security policy

## Supported version

Security fixes are applied to the latest commit on `main`. This reference application is not a
hosted resume service and does not promise long-term support for earlier commits.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for this repository. Do not open a public issue
containing an exploit, access token, real resume, job application, email address, phone number, or
other personal data. A maintainer will acknowledge a complete report and coordinate remediation and
disclosure through the private advisory.

## Data-handling boundary

Only synthetic fixtures belong in tests, issues, and pull requests. The application does not persist
uploaded bytes. A derived draft may remain in process memory for no longer than 15 minutes and is
removed when its single-use export token is consumed. Deployments that add durable storage, external
model providers, authentication, or telemetry must perform a separate security and privacy review.
