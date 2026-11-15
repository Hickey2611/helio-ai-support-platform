
import re

from sqlmodel import SQLModel, Field, Session, select


class KnowledgeBase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str


class KnowledgeCreate(SQLModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10, max_length=10000)


class KnowledgeRead(KnowledgeCreate):
    id: int


TOPICS = {
    "returns": {
        "return", "returns", "refund", "refunded",
        "money back", "exchange"
    },
    "shipping": {
        "shipping", "delivery", "delivered",
        "parcel", "package", "tracking",
        "shipment", "arrive", "arrived"
    },
    "security": {
        "password", "account", "login",
        "hacked", "fraud", "unauthorized",
        "security", "sign in"
    }
}

STOP_WORDS = {
    "the", "and", "for", "with", "this",
    "that", "what", "when", "where",
    "have", "your", "can", "how",
    "are", "from", "after", "about",
    "please", "want", "would", "could",
    "order", "customer", "days"
}


def tokenize(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) >= 3 and word not in STOP_WORDS
    }


def detect_topic(text: str) -> str | None:
    text = text.lower()
    words = tokenize(text)

    scores = {}

    for topic, keywords in TOPICS.items():
        scores[topic] = sum(
            1 for keyword in keywords
            if (
                keyword in words
                if " " not in keyword
                else keyword in text
            )
        )

    best_topic = max(scores, key=scores.get)

    if scores[best_topic] == 0:
        return None

    return best_topic


def rank_documents(
        documents: list[KnowledgeBase],
        query: str,
        limit: int = 3
) -> list[KnowledgeBase]:

    query_words = tokenize(query)
    query_topic = detect_topic(query)

    ranked = []

    for document in documents:
        title_words = tokenize(document.title)
        content_words = tokenize(document.content)

        doc_topic = detect_topic(document.title)

        # Prefer policies matching the main question topic.
        if query_topic and doc_topic:
            if query_topic != doc_topic:
                continue

        score = (
                5 * len(query_words & title_words)
                + len(query_words & content_words)
        )

        if query_topic and doc_topic == query_topic:
            score += 10

        if score > 0:
            ranked.append((score, document))

    ranked.sort(key=lambda item: item[0], reverse=True)

    return [
        document
        for score, document in ranked[:limit]
    ]


def search_knowledge(
        session: Session,
        query: str,
        limit: int = 3
) -> list[KnowledgeBase]:

    documents = session.exec(
        select(KnowledgeBase)
    ).all()

    return rank_documents(documents, query, limit)
