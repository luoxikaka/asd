from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from common.events.order_events import OrderCreatedEvent
from domain.entities.order import Order, OrderItem
from domain.repositories.order_repo import OrderRepository
from infrastructure.messaging.kafka_producer import EventPublisher


@dataclass(frozen=True)
class CreateOrderItemInput:
    sku_id: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: str
    items: List[CreateOrderItemInput]
    idempotency_key: str


@dataclass(frozen=True)
class CreateOrderResult:
    order_id: str
    total_amount: Decimal
    status: str


class CreateOrderUseCase:
    """创建订单核心流程。

    流程：
    1. 参数映射为领域对象
    2. 校验并创建订单聚合
    3. 落库
    4. 发布订单创建事件
    """

    def __init__(self, repo: OrderRepository, publisher: EventPublisher) -> None:
        self.repo = repo
        self.publisher = publisher

    def execute(self, cmd: CreateOrderCommand) -> CreateOrderResult:
        items = [
            OrderItem(
                sku_id=item.sku_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in cmd.items
        ]

        order = Order(user_id=cmd.user_id, items=items)
        self.repo.save(order)

        event = OrderCreatedEvent(
            event_name="OrderCreated",
            order_id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            created_at=order.created_at,
        )
        self.publisher.publish("order.created", event.to_message())

        return CreateOrderResult(
            order_id=order.id,
            total_amount=order.total_amount,
            status=order.status.value,
        )
