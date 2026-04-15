from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict

logger = logging.getLogger(__name__)


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: Dict[str, str]) -> None:
        ...


class KafkaOrderEventProducer(EventPublisher):
    """Kafka 生产者示例。

    当前为演示实现（打印日志），可替换为 confluent-kafka 或 aiokafka。
    """

    def publish(self, topic: str, payload: Dict[str, str]) -> None:
        logger.info("[Kafka] topic=%s payload=%s", topic, json.dumps(payload, ensure_ascii=False))
