# v3（真正大厂）落地模板

部署顺序（示例）：

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/platform-data.yaml
kubectl apply -f k8s/microservices.yaml
kubectl apply -f k8s/gateway-and-virtualservice.yaml
```

说明：
1. **API Gateway**：由 Istio Ingress Gateway 承担统一入口。
2. **Service Mesh**：通过 namespace label `istio-injection: enabled` 自动注入 sidecar。
3. **微服务集群**：`user-service` 与 `order-service` 多副本。
4. **分布式缓存**：`redis-cluster` StatefulSet。
5. **分库分表**：示例里提供 `db-router` 占位，生产建议替换为 Vitess / ShardingSphere。
