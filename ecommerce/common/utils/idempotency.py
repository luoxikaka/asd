from __future__ import annotations

from typing import Set


class InMemoryIdempotencyStore:
    """简化版幂等存储。

    生产环境应替换为 Redis / DB。
    """

    def __init__(self) -> None:
        self._keys: Set[str] = set()

    def is_processed(self, key: str) -> bool:
        return key in self._keys

    def mark_processed(self, key: str) -> None:
        self._keys.add(key)
