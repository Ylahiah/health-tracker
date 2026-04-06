from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.config import settings


def _get_tz() -> ZoneInfo:
    try:
        return ZoneInfo(getattr(settings, "TIMEZONE", "UTC") or "UTC")
    except Exception:
        return ZoneInfo("UTC")


def local_today() -> date:
    return datetime.now(_get_tz()).date()


def local_now() -> datetime:
    return datetime.now(_get_tz())


def format_date_es(d: date) -> str:
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    return f"{dias[d.weekday()]} {d.day} de {meses[d.month - 1]}"


def format_time_ampm(dt: datetime) -> str:
    h = dt.hour
    m = dt.minute
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m:02d} {suffix}"
