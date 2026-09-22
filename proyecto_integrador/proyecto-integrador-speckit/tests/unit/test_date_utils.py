from datetime import datetime, timezone, timedelta
from app.utils.date_utils import now_utc, to_iso_utc, parse_iso_datetime


def test_now_utc():
    now = now_utc()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc


def test_to_iso_utc():
    assert to_iso_utc(None) is None

    # Naive datetime
    naive_dt = datetime(2026, 9, 21, 15, 30, 0)
    iso_naive = to_iso_utc(naive_dt)
    assert iso_naive == "2026-09-21T15:30:00Z"

    # Aware datetime with offset
    offset = timezone(timedelta(hours=-5))
    aware_dt = datetime(2026, 9, 21, 10, 30, 0, tzinfo=offset)
    iso_aware = to_iso_utc(aware_dt)
    assert iso_aware == "2026-09-21T15:30:00Z"


def test_parse_iso_datetime():
    assert parse_iso_datetime(None) is None
    assert parse_iso_datetime("") is None
    assert parse_iso_datetime("   ") is None

    parsed = parse_iso_datetime("2026-09-21T15:30:00Z")
    assert parsed == datetime(2026, 9, 21, 15, 30, 0, tzinfo=timezone.utc)

    # Offset string
    parsed_offset = parse_iso_datetime("2026-09-21T10:30:00-05:00")
    assert parsed_offset == datetime(2026, 9, 21, 15, 30, 0, tzinfo=timezone.utc)
