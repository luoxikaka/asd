from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from usecases.create_order import (
    CreateOrderCommand,
    CreateOrderItemInput,
    CreateOrderUseCase,
)


class CreateOrderItemRequest(BaseModel):
    sku_id: str = Field(..., description="SKU 编号")
    quantity: int = Field(..., gt=0, description="购买数量")
    unit_price: Decimal = Field(..., gt=0, description="单价")


class CreateOrderRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    items: List[CreateOrderItemRequest]


class CreateOrderResponse(BaseModel):
    order_id: str
    total_amount: Decimal
    status: str


class OrderController:
    def __init__(self, usecase: CreateOrderUseCase) -> None:
        self.usecase = usecase

    def create_order(self, request: CreateOrderRequest, idempotency_key: str) -> CreateOrderResponse:
        cmd = CreateOrderCommand(
            user_id=request.user_id,
            items=[
                CreateOrderItemInput(
                    sku_id=item.sku_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in request.items
            ],
            idempotency_key=idempotency_key,
        )

        result = self.usecase.execute(cmd)
        return CreateOrderResponse(
            order_id=result.order_id,
            total_amount=result.total_amount,
            status=result.status,
        )
