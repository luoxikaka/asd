# 三套“最小可生产”架构代码

## v1（你现在就能搭）
- 目录：`v1/`
- 组件：Nginx -> FastAPI x3 -> Redis -> PostgreSQL
- 启动：

```bash
cd v1
docker compose up --build
```

## v2（进阶）
- 目录：`v2/`
- 组件：APISIX -> 多 FastAPI 服务 -> Redis(限流+缓存) -> PostgreSQL(主/从) -> RabbitMQ
- 启动：

```bash
cd v2
docker compose up --build
```

## v3（真正大厂）
- 目录：`v3/`
- 组件：API Gateway -> Service Mesh -> 微服务 -> 分布式缓存 + 分库分表
- 形态：Kubernetes + Istio manifests
