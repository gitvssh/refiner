import pytest
from refiner.core.ports import GrantNotFoundError
from refiner.infrastructure.adapters.export_grants import MemoryExportGrantStore


def test_grant_is_hashed_and_consumed_once() -> None:
    store = MemoryExportGrantStore(ttl_seconds=60)
    grant = store.issue("derived draft")

    assert grant.token not in repr(store)
    assert store.active_count() == 1
    assert store.consume(grant.token) == "derived draft"
    assert store.active_count() == 0
    with pytest.raises(GrantNotFoundError):
        store.consume(grant.token)


def test_expired_grant_is_not_returned() -> None:
    now = 10.0

    def clock() -> float:
        return now

    store = MemoryExportGrantStore(ttl_seconds=5, clock=clock)
    grant = store.issue("derived draft")
    now = 16.0

    with pytest.raises(GrantNotFoundError):
        store.consume(grant.token)
