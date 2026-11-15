
from fastapi import HTTPException
from sqlmodel import SQLModel, Field, Session, select

from app.models import Ticket


class TicketOwnership(SQLModel, table=True):
    ticket_id: int = Field(
        foreign_key="ticket.id",
        primary_key=True
    )
    user_id: int = Field(
        foreign_key="user.id",
        index=True
    )


def get_owned_ticket(
        session: Session,
        ticket_id: int,
        user_id: int
) -> Ticket:
    statement = (
        select(Ticket)
        .join(
            TicketOwnership,
            TicketOwnership.ticket_id == Ticket.id
        )
        .where(
            Ticket.id == ticket_id,
            TicketOwnership.user_id == user_id
        )
    )

    ticket = session.exec(statement).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket
