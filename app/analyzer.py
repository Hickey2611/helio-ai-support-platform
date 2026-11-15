
from pydantic import BaseModel


class TicketAnalysis(BaseModel):
    category: str
    priority: str
    suggested_response: str


def analyze_ticket(subject: str, message: str) -> TicketAnalysis:
    text = f"{subject} {message}".lower()

    if any(word in text for word in [
        "refund", "money back", "charged twice"
    ]):
        category = "Billing / Refund"
        response = (
            "I'm sorry about the payment issue. "
            "Please provide your order number so our team "
            "can review your refund request."
        )

    elif any(word in text for word in [
        "delivery", "not arrived", "late", "missing order"
    ]):
        category = "Delivery Issue"
        response = (
            "I'm sorry your order has not arrived. "
            "Please share your order number so our team "
            "can investigate the delivery status."
        )

    elif any(word in text for word in [
        "login", "password", "account", "cannot sign in"
    ]):
        category = "Account Issue"
        response = (
            "I'm sorry you're having trouble accessing "
            "your account. Please describe the issue "
            "without sharing your password."
        )

    else:
        category = "General Inquiry"
        response = (
            "Thank you for contacting us. "
            "Our support team will review your request."
        )

    if any(word in text for word in [
        "urgent", "immediately", "charged twice",
        "fraud", "3 days", "three days"
    ]):
        priority = "High"
    elif category in ["Billing / Refund", "Delivery Issue"]:
        priority = "Medium"
    else:
        priority = "Low"

    return TicketAnalysis(
        category=category,
        priority=priority,
        suggested_response=response
    )