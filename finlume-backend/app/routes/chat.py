from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models.models import User, Transaction
from app.schemas.schemas import ChatMessage, ChatReply
from app.routes.auth import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

def compute_local_summary(user_id: int, db: Session):
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expense = sum(t.amount for t in txs if t.type == "expense")
    net = total_income - total_expense
    
    by_category = {}
    for t in txs:
        if t.type == "expense":
            by_category[t.category] = by_category.get(t.category, 0.0) + t.amount
            
    top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net": net,
        "top_categories": top_categories,
        "txs_count": len(txs)
    }

from app.ai.orchestrator import call_orchestrator

@router.post("/", response_model=ChatReply)
def chat_with_coach(
    chat_in: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    message = chat_in.message.strip().lower()
    
    # Fetch raw transactions to pass to the orchestrator agents
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    txs_list = [
        {"amount": t.amount, "type": t.type, "category": t.category, "description": t.description}
        for t in txs
    ]
    
    summary = compute_local_summary(current_user.id, db)
    
    anthropic_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    
    if anthropic_key or gemini_key:
        try:
            result = call_orchestrator(current_user.id, chat_in.message, summary, txs_list)
            return ChatReply(reply=result["reply"], agents_used=result["agents_used"])
        except Exception as e:
            print(f"ORCHESTRATOR EXCEPTION: {e}")
            # Fall back to heuristic matching on API error (e.g. rate limit, network issue)
            pass

    # 2. Heuristic Rules-Based Advisor (matches Flask legacy logic)
    reply_parts = []
    income = summary["total_income"]
    expense = summary["total_expense"]
    net = summary["net"]

    if "summary" in message or "overview" in message:
        reply_parts.append(
            f"Here is your quick overview: your total income is ₹{income:.2f}, your expenses are ₹{expense:.2f}, and your net balance is ₹{net:.2f}."
        )

    if "save" in message or "savings" in message:
        if net <= 0:
            reply_parts.append(
                "Right now your expenses are equal to or higher than your income. Start by cutting 5–10% from non-essential categories like eating out or shopping."
            )
        else:
            target_savings = net * 0.5
            reply_parts.append(
                f"You can aim to save around ₹{target_savings:.2f} this month (about 50% of your surplus). Set up an automatic transfer on your salary date."
            )

    if "spend" in message or "expense" in message or "overspending" in message:
        if summary["top_categories"]:
            top = summary["top_categories"][0]
            cat, amt = top[0], top[1]
            reply_parts.append(
                f"Your highest expense category is {cat} at about ₹{amt:.2f}. Consider setting a hard monthly limit for this category."
            )
        else:
            reply_parts.append("You haven't recorded any expenses yet! Once you log some transactions, I'll tell you about your top spending categories.")

    if "goal" in message or "target" in message:
        reply_parts.append(
            "Try defining a clear goal like: 'Save ₹25,000 in 6 months for an emergency fund.' I can then remind you to stay on track each week."
        )

    if not reply_parts:
        helper_text = (
            "I analyzed your recent transactions. Ask me things like:\n"
            "• 'How much did I spend on food?'\n"
            "• 'Can I increase my savings this month?'\n"
            "• 'Give me a quick spending summary.'"
        )
        reply_parts.append(helper_text)

    return ChatReply(reply=" ".join(reply_parts), agents_used=[])
