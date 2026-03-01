from decimal import Decimal

from app.parser import parse_budget_command, parse_expense_message


def test_parse_expense_message_market():
    parsed = parse_expense_message("mercado 130")
    assert parsed is not None
    assert parsed.amount == Decimal("130")
    assert parsed.category == "alimentacao"


def test_parse_expense_message_transport():
    parsed = parse_expense_message("uber 22,50")
    assert parsed is not None
    assert parsed.amount == Decimal("22.50")
    assert parsed.category == "transporte"


def test_parse_budget_command():
    assert parse_budget_command("limite 2500") == Decimal("2500")
