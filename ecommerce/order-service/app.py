from __future__ import annotations

import logging

from fastapi import FastAPI, Header, HTTPException

from common.utils.idempotency import InMemoryIdempotencyStore
from infrastructure.db.mysql_repo import MySQLOrderRepository
from infrastructure.messaging.kafka_producer import KafkaOrderEventProducer
from interfaces.order_controller import CreateOrderRequest, CreateOrderResponse, OrderController
from usecases.create_order import CreateOrderUseCase

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="order-service", version="1.0.0")

# ===== 基础设施装配（Composition Root） =====
repo = MySQLOrderRepository()
publisher = KafkaOrderEventProducer()
usecase = CreateOrderUseCase(repo, publisher)
controller = OrderController(usecase)
idempotency_store = InMemoryIdempotencyStore()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/orders", response_model=CreateOrderResponse)
def create_order(
    request: CreateOrderRequest,
    x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
) -> CreateOrderResponse:
    if idempotency_store.is_processed(x_idempotency_key):
        raise HTTPException(status_code=409, detail="重复请求，请勿重试")

    response = controller.create_order(request, idempotency_key=x_idempotency_key)
    idempotency_store.mark_processed(x_idempotency_key)
    return response
