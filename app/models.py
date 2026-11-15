from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class TicketBase(SQLModel):
    customer_email: str = Field(min_length=3, max_length=255, index=True)
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=5)


class Ticket(TicketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: TicketStatus = Field(default=TicketStatus.open)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TicketCreate(TicketBase):
    pass


class TicketRead(TicketBase):
    id: int
    status: TicketStatus
    created_at: datetime


class TicketStatusUpdate(SQLModel):
    status: TicketStatus
