"""Pure timeline derivation from persisted WorkTrace rows."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TimelineEntry:
    trace_id: str
    occurred_at: str
    event_type: str
    work_item_id: str | None
    assignment_status: str
    duration_seconds: int | None
    source: str | None


def build_timeline(rows, *, include_unassigned=True):
    """Build a deterministic chronological view; never mutates domain facts."""
    entries=[]
    for row in rows:
        status=row["assignment_status"]
        if not include_unassigned and status == "unassigned":
            continue
        entries.append(TimelineEntry(row["trace_id"],row["occurred_at"],row["event_type"],row["work_item_id"],status,row["duration_seconds"],row["source"]))
    return sorted(entries,key=lambda x:(x.occurred_at,x.trace_id))
