
from app.knowledge import (
    KnowledgeBase,
    rank_documents
)


documents = [
    KnowledgeBase(
        id=1,
        title="Return Policy",
        content=(
            "Eligible products can be returned "
            "within 30 days for a refund."
        )
    ),
    KnowledgeBase(
        id=2,
        title="Shipping Policy",
        content=(
            "Delivery normally takes 3 to 5 "
            "business days. Track your package."
        )
    ),
    KnowledgeBase(
        id=3,
        title="Account Security Policy",
        content=(
            "Never share passwords. Report "
            "hacked accounts and fraud."
        )
    )
]


def test_return_search():
    result = rank_documents(
        documents,
        "Can I return my headphones for a refund?"
    )
    assert len(result) == 1
    assert result[0].title == "Return Policy"


def test_shipping_search():
    result = rank_documents(
        documents,
        "Where is my package delivery?"
    )
    assert len(result) == 1
    assert result[0].title == "Shipping Policy"


def test_security_search():
    result = rank_documents(
        documents,
        "My account was hacked"
    )
    assert len(result) == 1
    assert result[0].title == "Account Security Policy"


def test_empty_search():
    result = rank_documents(
        documents,
        "What is the weather on Mars?"
    )
    assert result == []


def test_result_limit():
    result = rank_documents(
        documents,
        "return refund",
        limit=1
    )
    assert len(result) <= 1
