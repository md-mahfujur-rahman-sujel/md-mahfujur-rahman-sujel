#!/usr/bin/env python3
"""Shared helpers for the profile asset generators."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "md-mahfujur-rahman-sujel")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
API = "https://api.github.com"
REPO_ROOT = Path(__file__).resolve().parent.parent
UA = "sujel-profile-dashboard/1.0"

PALETTE = ["#3B82F6", "#16263A", "#4F8DFF", "#A9C7FF", "#67C7EB"]
LANG_COLORS = {
    "HTML": "#3B82F6",
    "TypeScript": "#67C7EB",
    "JavaScript": "#A9C7FF",
    "Kotlin": "#4F8DFF",
    "CSS": "#93A6BA",
    "Java": "#4F8DFF",
    "Python": "#67C7EB",
}
# LANG_COLORS is for bars and dots only. Percentage labels are 12px text, so
# they need a lighter tint of the same hue to stay readable on the dark panel.
LANG_TEXT = {
    "HTML": "#93C5FD",
    "TypeScript": "#67C7EB",
    "JavaScript": "#A9C7FF",
    "Kotlin": "#BFDBFE",
    "CSS": "#93A6BA",
    "Java": "#BFDBFE",
    "Python": "#67C7EB",
}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def clip(value, limit: int) -> str:
    """Collapse whitespace and shorten to `limit` characters with an ellipsis.

    GitHub descriptions and branch names are unbounded; without a cap they run
    into the fixed right-hand columns of the panels.
    """
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: max(limit - 1, 0)].rstrip() + "…"


def warn(message: str) -> None:
    print(f"warning: {message}", flush=True)


def _request(url: str, data: bytes | None = None, timeout: int = 30):
    headers = {"User-Agent": UA}
    # Only api.github.com may receive the token and GitHub-specific headers.
    # `fetch_contributions` falls back to a third-party host; forwarding the
    # token there would leak it.
    if url.startswith(API):
        headers["Accept"] = "application/vnd.github+json"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def get_json(url: str, fallback=None, label: str = ""):
    try:
        return _request(url)
    except Exception as exc:  # noqa: BLE001 - the dashboard must always render
        warn(f"{label or url}: {exc}")
        return fallback


def post_graphql(query: str, variables: dict, fallback=None):
    if not TOKEN:
        return fallback
    try:
        payload = json.dumps({"query": query, "variables": variables}).encode()
        result = _request(f"{API}/graphql", data=payload)
        if result.get("errors"):
            raise RuntimeError(result["errors"][0].get("message", "GraphQL error"))
        return result
    except Exception as exc:  # noqa: BLE001
        warn(f"graphql: {exc}")
        return fallback


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def fetch_user(login: str = USER) -> dict:
    return get_json(f"{API}/users/{login}", fallback={}, label="user") or {}


def fetch_repos(login: str = USER) -> list[dict]:
    repos = get_json(
        f"{API}/users/{login}/repos?per_page=100&sort=pushed",
        fallback=[],
        label="repos",
    )
    return repos or []


def fetch_repo(full_name: str) -> dict:
    return get_json(f"{API}/repos/{full_name}", fallback={}, label=full_name) or {}


def fetch_languages(full_name: str) -> dict:
    return get_json(f"{API}/repos/{full_name}/languages", fallback={}, label=f"{full_name}/languages") or {}


def fetch_contributions(login: str = USER) -> tuple[list[dict], int, bool]:
    """Return (days, total, cached). Days are {date, count} dicts."""

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """
    result = post_graphql(query, {"login": login})
    if result:
        try:
            calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            days = [
                {"date": day["date"], "count": day["contributionCount"]}
                for week in calendar["weeks"]
                for day in week["contributionDays"]
            ]
            return days, int(calendar["totalContributions"]), False
        except (KeyError, TypeError):
            warn("graphql contribution calendar was empty")

    try:
        data = _request(f"https://github-contributions-api.jogruber.de/v4/{login}?y=last")
        days = [{"date": row["date"], "count": int(row["count"])} for row in data["contributions"]]
        total = data.get("total", {})
        total = total.get("lastYear", 0) if isinstance(total, dict) else int(total or 0)
        return days, int(total), False
    except Exception as exc:  # noqa: BLE001
        warn(f"contributions: {exc}")

    return fallback_days(), 0, True


def fallback_days() -> list[dict]:
    """Small snapshot used only when every contribution source is unreachable."""

    today = now_utc().date()
    start = today - dt.timedelta(days=370)
    counts = {
        "2026-07-29": 1,
        "2026-08-13": 3,
        "2026-08-17": 2,
        "2026-10-21": 3,
        "2026-10-22": 2,
        "2026-10-26": 4,
        "2026-10-27": 7,
    }
    days = []
    for index in range(371):
        day = start + dt.timedelta(days=index)
        days.append({"date": day.isoformat(), "count": counts.get(day.isoformat(), 0)})
    return days


def build_weeks(days: list[dict], count: int = 53) -> list[dict]:
    if not days:
        return []
    rows = sorted(days, key=lambda row: row["date"])
    end = dt.date.fromisoformat(rows[-1]["date"])
    start = end - dt.timedelta(days=count * 7 - 1)
    counts = {row["date"]: int(row["count"]) for row in rows}
    sequence = []
    for index in range(count * 7):
        day = start + dt.timedelta(days=index)
        sequence.append({"date": day.isoformat(), "count": counts.get(day.isoformat(), 0)})
    weeks = []
    for index in range(0, count * 7, 7):
        chunk = sequence[index : index + 7]
        weeks.append(
            {
                "start": dt.date.fromisoformat(chunk[0]["date"]),
                "days": chunk,
                "total": sum(day["count"] for day in chunk),
            }
        )
    return weeks


def contribution_stats(days: list[dict], total: int) -> dict:
    rows = sorted(days, key=lambda row: row["date"])
    active = [row for row in rows if row["count"] > 0]
    active_days = len(active)

    longest = 0
    longest_end = None
    current_run = 0
    previous = None
    for row in rows:
        day = dt.date.fromisoformat(row["date"])
        if row["count"] > 0:
            current_run = current_run + 1 if previous and (day - previous).days == 1 else 1
            if current_run > longest:
                longest = current_run
                longest_end = day
            previous = day
        else:
            current_run = 0
            previous = None

    current = 0
    current_end = None
    index = len(rows) - 1
    if index >= 0 and rows[index]["count"] == 0:
        index -= 1
    while index >= 0 and rows[index]["count"] > 0:
        if current_end is None:
            current_end = dt.date.fromisoformat(rows[index]["date"])
        current += 1
        index -= 1

    peak_row = max(rows, key=lambda row: row["count"]) if rows else {"count": 0, "date": ""}
    peak = int(peak_row["count"])
    peak_date = dt.date.fromisoformat(peak_row["date"]) if peak_row["date"] else None

    return {
        "total": int(total) if total else sum(row["count"] for row in rows),
        "active_days": active_days,
        "current": current,
        "current_start": current_end - dt.timedelta(days=current - 1) if current and current_end else None,
        "current_end": current_end,
        "longest": longest,
        "longest_start": longest_end - dt.timedelta(days=longest - 1) if longest and longest_end else None,
        "longest_end": longest_end,
        "peak": peak,
        "peak_date": peak_date,
    }


def fetch_language_totals(login: str = USER) -> list[tuple[str, int]]:
    totals: dict[str, int] = {}
    for repo in fetch_repos(login):
        if repo.get("fork"):
            continue
        languages = fetch_languages(repo["full_name"])
        for name, size in languages.items():
            totals[name] = totals.get(name, 0) + int(size)
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)


def fetch_events(login: str = USER) -> list[dict]:
    events = get_json(
        f"{API}/users/{login}/events/public?per_page=30",
        fallback=[],
        label="events",
    )
    return events or []


def stamp(moment: dt.datetime | None = None) -> str:
    moment = moment or now_utc()
    return moment.strftime("%d %b %Y · %H:%M UTC").upper()


def short_date(day: dt.date | None) -> str:
    return day.strftime("%b %d").upper() if day else "—"


def relative_day(value: str | None) -> str:
    if not value:
        return "—"
    try:
        day = dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return "—"
    delta = (now_utc().date() - day).days
    if delta <= 0:
        return "today"
    if delta == 1:
        return "1d ago"
    if delta < 31:
        return f"{delta}d ago"
    if delta < 365:
        return f"{delta // 30}mo ago"
    return f"{delta // 365}y ago"
