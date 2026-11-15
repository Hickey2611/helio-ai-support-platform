
from fastapi import HTTPException
from sqlmodel import SQLModel, Field, Session, select

from app.knowledge import KnowledgeBase, rank_documents


class KnowledgeOwnership(SQLModel, table=True):
    document_id: int = Field(
        foreign_key="knowledgebase.id",
        primary_key=True
    )
    user_id: int = Field(
        foreign_key="user.id",
        index=True
    )


def get_owned_document(
        session: Session,
        document_id: int,
        user_id: int
) -> KnowledgeBase:

    statement = (
        select(KnowledgeBase)
        .join(
            KnowledgeOwnership,
            KnowledgeOwnership.document_id == KnowledgeBase.id
        )
        .where(
            KnowledgeBase.id == document_id,
            KnowledgeOwnership.user_id == user_id
        )
    )

    document = session.exec(statement).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge document not found"
        )

    return document


def list_owned_documents(
        session: Session,
        user_id: int
) -> list[KnowledgeBase]:

    statement = (
        select(KnowledgeBase)
        .join(
            KnowledgeOwnership,
            KnowledgeOwnership.document_id == KnowledgeBase.id
        )
        .where(KnowledgeOwnership.user_id == user_id)
        .order_by(KnowledgeBase.id.desc())
    )

    return list(session.exec(statement).all())


def search_owned_knowledge(
        session: Session,
        user_id: int,
        query: str,
        limit: int = 3
) -> list[KnowledgeBase]:

    documents = list_owned_documents(
        session,
        user_id
    )

    return rank_documents(
        documents,
        query,
        limit
    )
