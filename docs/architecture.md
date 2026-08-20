# Architecture

## Dependency direction

```text
interfaces -> application -> core
                    ^          ^
                    |          |
              infrastructure adapters
```

`core/domain` owns pure normalization and keyword-coverage rules. `core/ports` describes the
analyzer, export-grant store, and PDF renderer without naming a framework or vendor.

`application/workflows` is reserved for the multi-stage refine path. Its nodes validate, analyze,
and rewrite explicit state. They do not know FastAPI or concrete storage. Use cases translate that
workflow into actions: refine an upload or consume an export grant.

`infrastructure/adapters` provides three local implementations:

- a deterministic analyzer for a credential-free demo;
- a lock-protected in-memory grant store with hashed tokens and atomic consume;
- a small PDF renderer using a built-in PDF font.

`interfaces/api` translates multipart HTTP input and errors. The composition root is the only place
where concrete adapters are selected.

## Why a workflow exists here

Refinement has ordered state transitions and an analyzer boundary that a real deployment could
replace with a model-backed adapter. Simple PDF export remains a direct use case. This distinction
keeps a graph or workflow abstraction from spreading into features that do not need one.

## Extension points

A model-backed analyzer should implement `AnalyzerPort`, receive settings through the composition
root, and keep provider-specific request types inside its adapter. It must not read environment
variables or log document content directly. A distributed deployment should replace the in-memory
grant store with an implementation that supports TTL and atomic consume.
