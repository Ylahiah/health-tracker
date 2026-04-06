from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd

from app.config import settings
from app.services import google_sheets_service as sheets
from app.utils import time_utils


@dataclass(frozen=True)
class FastingState:
    active: bool
    plan_hours: int
    start_at: datetime | None
    target_end_at: datetime | None
    elapsed: timedelta
    remaining: timedelta


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return None
        if isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()
        return dt
    except Exception:
        return None


def get_state(plan_hours: int = 16) -> FastingState:
    df = sheets.load_data(settings.SHEET_FASTING_LOG)
    now = time_utils.local_now()

    if df.empty:
        return FastingState(False, plan_hours, None, None, timedelta(0), timedelta(0))

    df = df.copy()
    df["start_at_dt"] = df["start_at"].apply(lambda x: _parse_dt(str(x) if x is not None else None))
    df["end_at_dt"] = df["end_at"].apply(lambda x: _parse_dt(str(x) if x is not None else None))
    df = df.dropna(subset=["start_at_dt"])
    if df.empty:
        return FastingState(False, plan_hours, None, None, timedelta(0), timedelta(0))

    df = df.sort_values(by="start_at_dt", ascending=True)
    active_df = df[(df["status"] == "Iniciado") & (df["end_at_dt"].isna())]

    if active_df.empty:
        return FastingState(False, plan_hours, None, None, timedelta(0), timedelta(0))

    last = active_df.iloc[-1].to_dict()
    start_at = last.get("start_at_dt")
    p = last.get("plan_hours")
    try:
        plan_h = int(p) if p not in [None, "", "nan"] else plan_hours
    except Exception:
        plan_h = plan_hours

    target_end = start_at + timedelta(hours=plan_h) if start_at else None
    elapsed = now - start_at if start_at else timedelta(0)
    remaining = target_end - now if target_end else timedelta(0)
    if remaining.total_seconds() < 0:
        remaining = timedelta(0)

    return FastingState(True, plan_h, start_at, target_end, elapsed, remaining)


def start_fast(plan_hours: int = 16, notes: str = "") -> bool:
    now = time_utils.local_now()
    row = {
        "date": str(time_utils.local_today()),
        "start_at": now.isoformat(),
        "end_at": "",
        "plan_hours": int(plan_hours),
        "status": "Iniciado",
        "notes": notes,
    }
    return sheets.add_row(settings.SHEET_FASTING_LOG, row)


def end_fast(notes: str = "") -> bool:
    state = get_state()
    if not state.active or not state.start_at:
        return False
    now = time_utils.local_now()
    row = {
        "date": str(time_utils.local_today()),
        "start_at": state.start_at.isoformat(),
        "end_at": now.isoformat(),
        "plan_hours": int(state.plan_hours),
        "status": "Finalizado",
        "notes": notes,
    }
    return sheets.add_row(settings.SHEET_FASTING_LOG, row)

