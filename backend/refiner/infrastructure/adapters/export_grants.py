from __future__ import annotations

import hashlib
import secrets
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from refiner.core.ports.export_grants import ExportGrant, GrantNotFoundError


@dataclass(frozen=True, slots=True)
class _GrantRecord:
    rewritten_resume: str
    expires_at: float


class MemoryExportGrantStore:
    def __init__(
        self,
        *,
        ttl_seconds: int = 15 * 60,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._records: dict[str, _GrantRecord] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def issue(self, rewritten_resume: str) -> ExportGrant:
        token = secrets.token_urlsafe(32)
        record = _GrantRecord(
            rewritten_resume=rewritten_resume,
            expires_at=self._clock() + self._ttl_seconds,
        )
        with self._lock:
            self._remove_expired_locked()
            self._records[self._digest(token)] = record
        return ExportGrant(token=token, expires_in_seconds=self._ttl_seconds)

    def consume(self, token: str) -> str:
        if len(token) < 32:
            raise GrantNotFoundError
        now = self._clock()
        with self._lock:
            self._remove_expired_locked(now)
            record = self._records.pop(self._digest(token), None)
        if record is None or record.expires_at <= now:
            raise GrantNotFoundError
        return record.rewritten_resume

    def _remove_expired_locked(self, now: float | None = None) -> None:
        current = self._clock() if now is None else now
        expired = [
            digest for digest, record in self._records.items() if record.expires_at <= current
        ]
        for digest in expired:
            del self._records[digest]

    def active_count(self) -> int:
        with self._lock:
            self._remove_expired_locked()
            return len(self._records)
