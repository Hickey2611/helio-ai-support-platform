from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select

from app.database import engine, get_session
from app.models import (
    Ticket,
    TicketCreate,
    TicketRead,
    TicketStatus,
    TicketStatusUpdate,
)
from app.auth import (
    User,
    router as auth_router,
    get_current_user,
)
from app.ownership import TicketOwnership, get_owned_ticket
from app.analyzer import analyze_ticket, TicketAnalysis
from app.ai_service import analyze_with_ai, AIAnalysis
from app.rag_service import generate_rag_answer
from app.knowledge import (
    KnowledgeBase,
    KnowledgeCreate,
    KnowledgeRead,
    search_knowledge,
)

from app.knowledge_access import (
    KnowledgeOwnership,
    get_owned_document,
    list_owned_documents,
    search_owned_knowledge,
)


# APPLICATION SETUP

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Development only. Use Alembic migrations later.
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="AI Support Automation Platform",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# TICKET MANAGEMENT

@app.post(
    "/tickets",
    response_model=TicketRead,
    status_code=201,
)
def create_ticket(
        data: TicketCreate,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    ticket = Ticket.model_validate(data)

    session.add(ticket)
    session.flush()

    ownership = TicketOwnership(
        ticket_id=ticket.id,
        user_id=user.id,
    )

    session.add(ownership)
    session.commit()
    session.refresh(ticket)

    return ticket


@app.get(
    "/tickets",
    response_model=list[TicketRead],
)
def list_tickets(
        status: TicketStatus | None = None,
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    statement = (
        select(Ticket)
        .join(
            TicketOwnership,
            TicketOwnership.ticket_id == Ticket.id,
        )
        .where(TicketOwnership.user_id == user.id)
    )

    if status is not None:
        statement = statement.where(
            Ticket.status == status
        )

    statement = (
        statement
        .order_by(Ticket.id.desc())
        .offset(offset)
        .limit(limit)
    )

    return session.exec(statement).all()


@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketRead,
)
def get_ticket(
        ticket_id: int,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    return get_owned_ticket(
        session,
        ticket_id,
        user.id,
    )


@app.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketRead,
)
def update_ticket_status(
        ticket_id: int,
        data: TicketStatusUpdate,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    ticket = get_owned_ticket(
        session,
        ticket_id,
        user.id,
    )

    ticket.status = data.status

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


# RULE-BASED ANALYSIS

@app.post(
    "/tickets/{ticket_id}/analyze",
    response_model=TicketAnalysis,
)
def analyze_existing_ticket(
        ticket_id: int,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    ticket = get_owned_ticket(
        session,
        ticket_id,
        user.id,
    )

    return analyze_ticket(
        subject=ticket.subject,
        message=ticket.message,
    )


# AI ANALYSIS

@app.post(
    "/tickets/{ticket_id}/ai-analyze",
    response_model=AIAnalysis,
)
def analyze_ticket_ai(
        ticket_id: int,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    ticket = get_owned_ticket(
        session,
        ticket_id,
        user.id,
    )

    try:
        return analyze_with_ai(
            subject=ticket.subject,
            message=ticket.message,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable",
        ) from error


# KNOWLEDGE BASE

@app.post(
    "/knowledge",
    response_model=KnowledgeRead,
    status_code=201,
)
def add_knowledge(
        data: KnowledgeCreate,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    document = KnowledgeBase.model_validate(data)

    session.add(document)
    session.flush()

    ownership = KnowledgeOwnership(
        document_id=document.id,
        user_id=user.id,
    )

    session.add(ownership)
    session.commit()
    session.refresh(document)

    return document


@app.get(
    "/knowledge",
    response_model=list[KnowledgeRead],
)
def list_knowledge(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    return list_owned_documents(
        session,
        user.id,
    )


@app.get(
    "/knowledge/search",
    response_model=list[KnowledgeRead],
)
def find_knowledge(
        q: str = Query(min_length=3),
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    return search_owned_knowledge(
        session,
        user.id,
        q,
    )


@app.delete(
    "/knowledge/{document_id}",
    status_code=204,
)
def delete_knowledge(
        document_id: int,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    document = get_owned_document(
        session,
        document_id,
        user.id,
    )

    # Delete ownership before deleting document
    ownership = session.get(
        KnowledgeOwnership,
        document_id,
    )

    session.delete(ownership)
    session.delete(document)
    session.commit()


@app.put(
    "/knowledge/{document_id}",
    response_model=KnowledgeRead,
)
def update_knowledge(
        document_id: int,
        data: KnowledgeCreate,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    document = get_owned_document(
        session,
        document_id,
        user.id,
    )

    document.title = data.title
    document.content = data.content

    session.add(document)
    session.commit()
    session.refresh(document)

    return document


# RAG ANALYSIS

class RAGResult(BaseModel):
    answer: str
    sources: list[str]
    grounded: bool


@app.post(
    "/tickets/{ticket_id}/rag-analyze",
    response_model=RAGResult,
)
def analyze_ticket_with_rag(
        ticket_id: int,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    ticket = get_owned_ticket(
        session,
        ticket_id,
        user.id,
    )

    documents = search_owned_knowledge(
        session=session,
        user_id=user.id,
        query=f"{ticket.subject} {ticket.message}",
    )

    if not documents:
        return RAGResult(
            answer=(
                "Our support team needs to review "
                "your request because no relevant "
                "company policy was found."
            ),
            sources=[],
            grounded=False,
        )

    try:
        answer = generate_rag_answer(
            subject=ticket.subject,
            message=ticket.message,
            documents=documents,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable",
        ) from error

    return RAGResult(
        answer=answer,
        sources=[doc.title for doc in documents],
        grounded=True,
    )
