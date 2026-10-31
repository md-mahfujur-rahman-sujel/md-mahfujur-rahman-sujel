#!/usr/bin/env python3
"""Render the live public activity feed (assets/activity.svg)."""

from __future__ import annotations

import datetime as dt

from common import REPO_ROOT, USER, clip, corner_web, esc, fetch_events, now_utc, spider, stamp

W, H = 1280, 430
M = 56.0
CONTENT_W = W - M * 2
ROW_TOP = 160.0
ROW_STEP = 32.0
RAIL_X = 166.0
EVENTS = 7

BADGES = {
    "PushEvent": ("PUSH", "#FFB4B4"),
    "CreateEvent": ("CREATE", "#6C9FE0"),
    "PublicEvent": ("PUBLIC", "#FF6B6B"),
    "WatchEvent": ("STAR", "#FFB4B4"),
    "ForkEvent": ("FORK", "#FF6B6B"),
    "PullRequestEvent": ("PR", "#FF6B6B"),
    "IssuesEvent": ("ISSUE", "#FF6B6B"),
    "ReleaseEvent": ("RELEASE", "#6C9FE0"),
    "DeleteEvent": ("DELETE", "#FF6B6B"),
    "CommitCommentEvent": ("COMMENT", "#6C9FE0"),
    "IssueCommentEvent": ("COMMENT", "#6C9FE0"),
}

FALLBACK = [
    {"type": "PublicEvent", "repo": "Apex-Arcade", "text": "published repository to public", "at": "2026-10-21T12:38:37Z"},
    {"type": "PushEvent", "repo": "Unrot", "text": "pushed 3 commits", "at": "2026-10-22T17:57:53Z"},
    {"type": "CreateEvent", "repo": "Unrot", "text": "created branch main", "at": "2026-10-27T03:11:22Z"},
    {"type": "PushEvent", "repo": "Unrot", "text": "pushed 2 commits", "at": "2026-10-27T03:17:44Z"},
]

CSS = """
.s{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
.m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.rise{animation:rise .6s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(8px)}}
@media (prefers-reduced-motion:reduce){.pulse,.rise{animation:none!important}}
"""


def describe(event: dict) -> str:
    kind = event.get("type", "")
    payload = event.get("payload") or {}
    if kind == "PushEvent":
        count = payload.get("size") or len(payload.get("commits") or []) or 1
        return f"pushed {count} commit{'s' if count != 1 else ''}"
    if kind == "CreateEvent":
        ref_type = payload.get("ref_type") or "ref"
        ref = payload.get("ref")
        return f"created {ref_type} {ref}" if ref else f"created {ref_type}"
    if kind == "PublicEvent":
        return "published repository to public"
    if kind == "WatchEvent":
        return "starred repository"
    if kind == "ForkEvent":
        return "forked repository"
    if kind == "PullRequestEvent":
        return f"{payload.get('action') or 'updated'} pull request #{payload.get('number') or '—'}"
    if kind == "IssuesEvent":
        return f"{payload.get('action') or 'updated'} issue #{payload.get('number') or '—'}"
    if kind == "ReleaseEvent":
        return f"published release {(payload.get('release') or {}).get('tag_name') or '—'}"
    if kind == "DeleteEvent":
        return f"deleted {payload.get('ref_type') or 'ref'} {payload.get('ref') or ''}".strip()
    if kind == "CommitCommentEvent":
        return "commented on a commit"
    if kind == "IssueCommentEvent":
        return "commented on an issue"
    return (kind.replace("Event", "").lower() or "event") + " recorded"


def ago(value: str | None) -> str:
    if not value:
        return "—"
    try:
        moment = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "—"
    seconds = (now_utc() - moment).total_seconds()
    if seconds < 0:
        return "JUST NOW"
    if seconds < 3600:
        minutes = max(int(seconds // 60), 1)
        return f"{minutes}M AGO" if minutes > 1 else "JUST NOW"
    if seconds < 86400:
        return f"{int(seconds // 3600)}H AGO"
    if seconds < 604800:
        return f"{int(seconds // 86400)}D AGO"
    return moment.strftime("%b %d").upper()


def entries() -> tuple[list[dict], bool]:
    events = sorted(fetch_events(), key=lambda event: event.get("created_at", ""), reverse=True)
    rows = []
    for event in events:
        kind = event.get("type", "")
        if kind not in BADGES:
            continue
        repo = (event.get("repo") or {}).get("name", "").split("/")[-1] or "github"
        rows.append(
            {
                "type": kind,
                "repo": repo,
                "text": describe(event),
                "at": event.get("created_at", ""),
            }
        )
        if len(rows) == EVENTS:
            break
    if not rows:
        return sorted(FALLBACK, key=lambda row: row["at"], reverse=True), True
    return rows, False


def render() -> str:
    now = now_utc()
    rows, cached = entries()

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Recent public GitHub activity for {esc(USER)}">'
    )
    out.append("<defs>")
    out.append('<linearGradient id="bg" x1="0" y1="0" x2=".85" y2="1"><stop offset="0" stop-color="#070C16"/><stop offset=".55" stop-color="#0A1223"/><stop offset="1" stop-color="#060A13"/></linearGradient>')
    out.append('<radialGradient id="glowRed"><stop offset="0" stop-color="#D9232E" stop-opacity=".16"/><stop offset="1" stop-color="#D9232E" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="glowBlue"><stop offset="0" stop-color="#6C9FE0" stop-opacity=".12"/><stop offset="1" stop-color="#6C9FE0" stop-opacity="0"/></radialGradient>')
    out.append(f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>')
    out.append(f"<style>{CSS}</style>")
    out.append("</defs>")

    out.append('<g clip-path="url(#frame)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append('<ellipse cx="80" cy="430" rx="460" ry="280" fill="url(#glowRed)"/>')
    out.append('<ellipse cx="1230" cy="0" rx="380" ry="240" fill="url(#glowBlue)"/>')
    out.append(corner_web(1288, 22, 205, spokes=9, rings=(0.42, 0.72, 1.0), rotation=2.2, opacity=0.13, width=1.5))
    out.append(spider(676, 60, 1.0, thread=60, opacity=0.5))

    out.append('<g class="rise">')
    out.append('<circle class="pulse" cx="62" cy="48" r="3.5" fill="#D9232E"/>')
    out.append('<text class="m" x="78" y="52" font-size="11" letter-spacing="2.6" fill="#FF9A9A">PUBLIC FEED</text>')
    out.append('<text class="s" x="56" y="106" font-size="32" font-weight="800" letter-spacing="-.4" fill="#F5F8FC">Signals</text>')
    out.append(
        f'<text class="m" x="1224" y="52" text-anchor="end" font-size="10.5" fill="#8FA1B6">'
        f'{len(rows):02d} EVENTS · AUTO-SYNC EVERY 3H</text>'
    )
    out.append(f'<text class="m" x="1224" y="106" text-anchor="end" font-size="10.5" fill="#6D7E94">{esc(stamp(now))}</text>')
    out.append(f'<rect x="{M}" y="124" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".8"/>')
    out.append("</g>")

    rail_top = ROW_TOP - 18
    rail_bottom = ROW_TOP + (EVENTS - 1) * ROW_STEP + 12
    out.append(f'<rect x="{RAIL_X - 0.5}" y="{rail_top:.1f}" width="1" height="{rail_bottom - rail_top:.1f}" fill="#1E2C48" fill-opacity=".8"/>')

    for index, row in enumerate(rows):
        baseline = ROW_TOP + index * ROW_STEP
        label, color = BADGES.get(row["type"], ("EVENT", "#8FA1B6"))
        tint = "#FFDADA" if color == "#D9232E" else color
        out.append(f'<g class="rise" style="animation-delay:{0.05 + 0.05 * index:.2f}s">')
        try:
            moment = dt.datetime.fromisoformat(row["at"].replace("Z", "+00:00"))
            when = moment.strftime("%d %b · %H:%M").upper()
        except (ValueError, AttributeError):
            when = "—"
        out.append(f'<text class="m" x="{RAIL_X - 24:.1f}" y="{baseline:.1f}" text-anchor="end" font-size="10.5" fill="#6D7E94">{ago(row["at"])}</text>')
        out.append(f'<circle cx="{RAIL_X}" cy="{baseline - 4:.1f}" r="4" fill="#0A1223" stroke="{color}" stroke-width="1.6"/>')
        out.append(f'<text class="m" x="{RAIL_X + 22:.1f}" y="{baseline:.1f}" font-size="10" letter-spacing="1.8" fill="{tint}">{label}</text>')
        out.append(
            f'<text class="s" x="{RAIL_X + 118:.1f}" y="{baseline:.1f}" font-size="14" fill="#E7EEF7">'
            f'{esc(clip(row["text"], 70))}<tspan fill="{tint}" fill-opacity=".9">  ·  {esc(clip(row["repo"], 40))}</tspan></text>'
        )
        out.append(f'<text class="m" x="1224" y="{baseline:.1f}" text-anchor="end" font-size="10.5" fill="#6D7E94">{when}</text>')
        out.append("</g>")

    status = "CACHED SNAPSHOT" if cached else "STREAM OK"
    status_color = "#C08A1E" if cached else "#6C9FE0"
    out.append(f'<rect x="{M}" y="376" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".7"/>')
    out.append(f'<circle class="pulse" cx="62" cy="404" r="3" fill="{status_color}"/>')
    out.append(f'<text class="m" x="76" y="408" font-size="11" fill="{status_color}">{status}</text>')
    out.append(f'<text class="m" x="196" y="408" font-size="11" fill="#8FA1B6">public events · newest first</text>')
    out.append(f'<text class="m" x="1224" y="408" text-anchor="end" font-size="11" fill="#6D7E94">github.com/{esc(USER)}</text>')

    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#1E2C48" stroke-opacity=".4"/>')
    out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    target = REPO_ROOT / "assets" / "activity.svg"
    target.write_text(render(), encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
