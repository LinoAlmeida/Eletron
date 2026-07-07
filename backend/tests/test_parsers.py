from datetime import date, time
from decimal import Decimal

from scripts.transform_reservas import to_date, to_decimal, to_time


def test_to_date_from_hfsql_yyyymmdd() -> None:
    assert to_date("20230401") == date(2023, 4, 1)


def test_to_time_from_hfsql_hhmmss() -> None:
    assert to_time("141959") == time(14, 19, 59)


def test_to_decimal_accepts_dot_and_comma() -> None:
    assert to_decimal("379.9") == Decimal("379.9")
    assert to_decimal("379,9") == Decimal("379.9")
