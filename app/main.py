"""FastAPI app with webhook endpoint for WhatsApp financial assistant."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI
from pydantic import BaseModel

from app.db import add_expense, get_budget, get_month_total, set_budget
from app.parser import is_monthly_summary_question, parse_budget_command, parse_expense_message

app = FastAPI(title="Assistente Financeiro WhatsApp")


class IncomingMessage(BaseModel):
    phone: str
    text: str
    media_type: str | None = None


class BotResponse(BaseModel):
    reply: str


def _format_brl(value: Decimal) -> str:
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook", response_model=BotResponse)
def webhook(payload: IncomingMessage) -> BotResponse:
    text = payload.text.strip()

    # Placeholder for OCR/STT pipeline hooks.
    if payload.media_type in {"image", "audio"}:
        return BotResponse(
            reply=(
                "Recebi sua mídia. Em produção, vou extrair os dados com OCR/STT e registrar automaticamente."
            )
        )

    budget = parse_budget_command(text)
    if budget is not None:
        set_budget(payload.phone, budget)
        return BotResponse(reply=f"Limite mensal definido em {_format_brl(budget)}.")

    if is_monthly_summary_question(text):
        month_prefix = datetime.utcnow().strftime("%Y-%m")
        total = get_month_total(payload.phone, month_prefix)
        existing_budget = get_budget(payload.phone)
        if existing_budget is None:
            return BotResponse(reply=f"Seu total no mês é {_format_brl(total)}. Ainda não há um limite definido.")
        remaining = existing_budget - total
        return BotResponse(
            reply=(
                f"Você já gastou {_format_brl(total)} neste mês. "
                f"Saldo disponível: {_format_brl(remaining)} de {_format_brl(existing_budget)}."
            )
        )

    expense = parse_expense_message(text)
    if expense is not None:
        add_expense(payload.phone, expense.description, expense.category, expense.amount)
        return BotResponse(
            reply=(
                f"Gasto registrado: {expense.description} | categoria {expense.category} | "
                f"valor {_format_brl(expense.amount)}."
            )
        )

    return BotResponse(
        reply=(
            "Não consegui entender. Envie no formato 'mercado 130', peça 'quanto gastei no mês' "
            "ou defina 'limite 2000'."
        )
    )
