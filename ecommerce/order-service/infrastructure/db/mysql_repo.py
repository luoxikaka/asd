from __future__ import annotations

from typing import Dict, Optional

from domain.entities.order import Order
from domain.repositories.order_repo import OrderRepository


class MySQLOrderRepository(OrderRepository):
    """MySQL 仓储示例。

    为了方便本地运行，这里先用内存字典模拟 DB。
    生产环境可替换为 SQLAlchemy + MySQL。
    """

    def __init__(self) -> None:
        self._store: Dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._store.get(order_id)
