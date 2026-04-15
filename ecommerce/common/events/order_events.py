from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict


@dataclass(frozen=True)
class OrderCreatedEvent:
    event_name: str
    order_id: str
    user_id: str
    total_amount: Decimal
    created_at: datetime

    def to_message(self) -> Dict[str, str]:
        payload = asdict(self)
        payload["total_amount"] = str(self.total_amount)
        payload["created_at"] = self.created_at.isoformat()
        return payload
