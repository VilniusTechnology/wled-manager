"""
Grandfather-Father-Son (time-machine) backup retention policy.

Shared policy between the WLED manager and the Tasmota manager. The two
managers live in separate repositories, so this module is duplicated in each;
the bucket thresholds and algorithm MUST be kept in sync.

Retention buckets (age = now - backup creation time), newest-first:

    * < 7 days      -> keep every backup            (fresh recovery window)
    * 7d .. 30d     -> keep the newest per day       (guarantees the "1 week" anchor)
    * 30d .. 90d    -> keep the newest per ISO week  (guarantees the "1 month" anchor)
    * 90d .. 365d   -> keep the newest per month     (guarantees "3 months" and "6 months")
    * >= 365d       -> keep the newest per year      (guarantees the "1 year" anchor)

This ensures at least one retained backup exists from roughly 1 week, 1 month,
3 months, 6 months and 1 year ago, while never deleting the only backup a
device has.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable, Iterable, List, Optional, TypeVar

logger = logging.getLogger(__name__)

# Age thresholds (days).
KEEP_ALL_DAYS = 7    # everything newer than this is kept verbatim
DAILY_DAYS = 30      # up to this age: one per day
WEEKLY_DAYS = 90     # up to this age: one per ISO week
MONTHLY_DAYS = 365   # up to this age: one per calendar month; beyond: one per year

T = TypeVar("T")


def _to_naive_utc(dt: datetime) -> datetime:
    """Normalize a datetime to naive UTC for safe age comparisons."""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


def _bucket_key(created: datetime, now: datetime):
    """Return the retention bucket key for a backup, or None if it must be kept."""
    age_days = (now - created).total_seconds() / 86400.0
    if age_days < KEEP_ALL_DAYS:
        return None
    if age_days < DAILY_DAYS:
        return ("day", created.year, created.month, created.day)
    if age_days < WEEKLY_DAYS:
        iso = created.isocalendar()
        return ("week", iso[0], iso[1])
    if age_days < MONTHLY_DAYS:
        return ("month", created.year, created.month)
    return ("year", created.year)


def parse_wled_timestamp(value) -> datetime:
    """Parse a WLED backup timestamp (stored as a string) into a naive datetime."""
    if isinstance(value, datetime):
        return _to_naive_utc(value)

    text = str(value or "").strip()
    # Format used by WLEDBackupRetriever: YYYYMMDD_HHMMSS
    for fmt in ("%Y%m%d_%H%M%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text.split(".")[0].replace("Z", ""), fmt)
        except ValueError:
            continue

    # ISO-8601 fallback (with or without timezone offset)
    try:
        iso = text.replace("Z", "+00:00")
        return _to_naive_utc(datetime.fromisoformat(iso))
    except ValueError:
        raise ValueError(f"Unparseable WLED backup timestamp: {value!r}")


def select_backups_for_deletion(
    backups: Iterable[T],
    timestamp: Callable[[T], datetime],
    now: Optional[datetime] = None,
) -> List[T]:
    """
    Return the subset of ``backups`` that should be deleted under the GFS policy.

    For every bucket that is older than ``KEEP_ALL_DAYS``, the newest backup in
    that bucket is retained and the rest are returned for deletion. Backups
    younger than ``KEEP_ALL_DAYS`` are always kept. If a device has zero or one
    backup, nothing is ever returned.

    Args:
        backups: Iterable of backup records.
        timestamp: Callable returning a ``datetime`` for a backup record.
        now: Reference "now" (defaults to ``datetime.utcnow()``).

    Returns:
        List of backup records to delete.
    """
    if now is None:
        now = _to_naive_utc(datetime.utcnow())

    items = list(backups)
    if len(items) <= 1:
        return []

    groups: dict = defaultdict(list)
    for item in items:
        created = _to_naive_utc(timestamp(item))
        groups[_bucket_key(created, now)].append(item)

    to_delete: List[T] = []
    for key, group in groups.items():
        if key is None:
            # Recent window: keep every backup.
            continue
        group.sort(key=lambda i: _to_naive_utc(timestamp(i)), reverse=True)
        # Keep the newest in the bucket; delete the rest.
        to_delete.extend(group[1:])

    return to_delete
