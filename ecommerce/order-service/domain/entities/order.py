from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List
from uuid import uuid4


class OrderStatus(str, Enum):
    """订单状态机（可按业务扩展）"""

    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    CANCELED = "CANCELED"


@dataclass(frozen=True)
class OrderItem:
    """订单项值对象"""

    sku_id: str
    quantity: int
    unit_price: Decimal

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    """订单聚合根。

    领域规则：
    1. 至少一个商品项
    2. 商品数量必须 > 0
    3. 总价自动根据商品项计算
    """

    user_id: str
    items: List[OrderItem]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("订单至少包含一个商品")
        for item in self.items:
            if item.quantity <= 0:
                raise ValueError("商品数量必须大于 0")

    @property
    def total_amount(self) -> Decimal:
        return sum((item.line_total for item in self.items), start=Decimal("0"))

    def mark_paid(self) -> None:
        if self.status == OrderStatus.CANCELED:
            raise ValueError("已取消订单不能支付")
        self.status = OrderStatus.PAID

    def cancel(self) -> None:
        if self.status == OrderStatus.PAID:
            raise ValueError("已支付订单不能取消")
        self.status = OrderStatus.CANCELED
