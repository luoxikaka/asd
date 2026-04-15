from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.order import Order


class OrderRepository(ABC):
    """订单仓储抽象接口（端口）"""

    @abstractmethod
    def save(self, order: Order) -> None:
        """持久化订单"""

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """根据订单ID查询订单"""
