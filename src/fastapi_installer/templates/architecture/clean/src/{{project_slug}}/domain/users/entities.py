from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class User:
    email: str
    full_name: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
