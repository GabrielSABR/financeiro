"""Utilities for extracting expenses and commands from WhatsApp messages."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

CATEGORY_KEYWORDS = {
    "alimentacao": {"mercado", "supermercado", "comida", "restaurante", "ifood", "lanche", "alimentacao"},
    "transporte": {"uber", "99", "taxi", "onibus", "metro", "combustivel", "gasolina", "transporte"},
    "lazer": {"cinema", "show", "viagem", "lazer", "streaming", "netflix", "spotify"},
    "saude": {"farmacia", "medico", "consulta", "saude", "academia", "plano"},
    "investimentos": {"investimento", "acao", "tesouro", "cripto", "fii", "aporte"},
    "outros": set(),
}


@dataclass
class ParsedExpense:
    description: str
    amount: Decimal
    category: str


def normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower().strip()


def parse_amount(text: str) -> Optional[Decimal]:
    match = re.search(r"(\d+[\.,]?\d{0,2})", text)
    if not match:
        return None
    amount_str = match.group(1).replace(".", "").replace(",", ".")
    try:
        value = Decimal(amount_str)
    except InvalidOperation:
        return None
    return value if value > 0 else None


def infer_category(description: str) -> str:
    tokens = set(normalize(description).split())
    for category, keywords in CATEGORY_KEYWORDS.items():
        if tokens.intersection(keywords):
            return category
    return "outros"


def parse_expense_message(message_text: str) -> Optional[ParsedExpense]:
    amount = parse_amount(message_text)
    if amount is None:
        return None

    normalized_text = normalize(message_text)
    description = re.sub(r"\d+[\.,]?\d{0,2}", "", normalized_text).strip() or "gasto"
    category = infer_category(description)
    return ParsedExpense(description=description, amount=amount, category=category)


def is_monthly_summary_question(message_text: str) -> bool:
    text = normalize(message_text)
    patterns = ["quanto gastei", "gastei esse mes", "resumo do mes", "total do mes"]
    return any(p in text for p in patterns)


def parse_budget_command(message_text: str) -> Optional[Decimal]:
    text = normalize(message_text)
    if "limite" not in text and "orcamento" not in text:
        return None
    return parse_amount(text)
