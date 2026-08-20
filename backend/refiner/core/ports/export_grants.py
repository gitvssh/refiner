from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class GrantNotFoundError(LookupError):
    """The grant is invalid, expired, or has already been consumed."""


@dataclass(frozen=True, slots=True)
class ExportGrant:
    token: str
    expires_in_seconds: int


class ExportGrantStorePort(Protocol):
    def issue(self, rewritten_resume: str) -> ExportGrant: ...

    def consume(self, token: str) -> str: ...
