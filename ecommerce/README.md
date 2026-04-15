# E-commerce 微服务示例（Clean Architecture + DDD）

这是一个按你给出的目录实现的可运行示例，重点演示 `order-service` 的分层职责与代码组织方式。

## 目录结构

```text
ecommerce/
├── gateway/
│   └── app.py
├── order-service/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── order.py
│   │   └── repositories/
│   │       └── order_repo.py
│   ├── usecases/
│   │   └── create_order.py
│   ├── interfaces/
│   │   └── order_controller.py
│   ├── infrastructure/
│   │   ├── db/
│   │   │   └── mysql_repo.py
│   │   └── messaging/
│   │       └── kafka_producer.py
│   └── app.py
├── payment-service/
│   └── app.py
├── user-service/
│   └── app.py
└── common/
    ├── events/
    │   └── order_events.py
    └── utils/
        └── idempotency.py
```

---

## 分层解释（以 order-service 为核心）

### 1) Domain（领域层）
- 只表达业务概念，不依赖框架。
- `Order` 是聚合根，包含状态、商品项、总价计算、状态流转规则（支付/取消）。
- `OrderRepository` 是仓储抽象（端口），定义“需要什么能力”，不关心“怎么实现”。

### 2) UseCases（用例层）
- 编排业务流程。
- `CreateOrderUseCase` 做四件事：
  1. DTO 转换为领域对象。
  2. 构建订单并触发领域校验。
  3. 调用仓储保存。
  4. 发布 `OrderCreated` 事件。

### 3) Interfaces（接口层）
- 面向 HTTP / RPC 输入输出。
- `OrderController` 负责：
  - 接收请求 DTO
  - 调用用例
  - 返回响应 DTO
- 这里不写数据库细节，也不写消息中间件细节。

### 4) Infrastructure（基础设施层）
- 对接外部系统（MySQL/Kafka/Redis 等）。
- `MySQLOrderRepository` 当前用内存字典模拟，便于快速启动。
- `KafkaOrderEventProducer` 当前用日志模拟事件发送。

### 5) App（启动入口）
- 组合根（Composition Root）：把抽象接口和具体实现装配在一起。
- 包含 FastAPI 路由与幂等处理（`X-Idempotency-Key`）。

---

## 快速启动

> 建议在 `ecommerce/order-service` 目录运行。

```bash
pip install -r ../../requirements.txt
uvicorn app:app --reload --port 8001
```

接口：
- `GET /health`
- `POST /orders`

### 创建订单请求示例

```bash
curl -X POST 'http://127.0.0.1:8001/orders' \
  -H 'Content-Type: application/json' \
  -H 'X-Idempotency-Key: create-order-001' \
  -d '{
    "user_id": "u_1001",
    "items": [
      {"sku_id": "sku_a", "quantity": 2, "unit_price": 19.90},
      {"sku_id": "sku_b", "quantity": 1, "unit_price": 49.00}
    ]
  }'
```

返回示例：

```json
{
  "order_id": "f8f39e18-0a3d-44c0-8a5a-0df2c31f2f06",
  "total_amount": 88.8,
  "status": "PENDING_PAYMENT"
}
```

---

## 生产化建议（下一步可扩展）

1. **仓储层**：用 SQLAlchemy + MySQL 实现真正持久化。
2. **事件可靠性**：引入 Outbox Pattern，保障“写库 + 发消息”一致性。
3. **幂等性**：将内存幂等替换为 Redis，并设置 TTL。
4. **API 网关**：增加鉴权（JWT/OAuth2）、限流、路由聚合、链路追踪。
5. **配置管理**：环境变量 + pydantic-settings。
6. **测试体系**：补充 domain/usecase 单测与接口集成测试。
