#!/usr/bin/env python3
"""Render the live public activity feed (assets/activity.svg)."""

from __future__ import annotations

import datetime as dt

from common import REPO_ROOT, USER, clip, esc, fetch_events, now_utc, stamp

W, H = 1280, 384
LOG_TOP = 88.0
FOOTER = H - 42

BADGES = {
    "PushEvent": ("PUSH", "#FFB4B4"),
    "CreateEvent": ("CREATE", "#6C9FE0"),
    "PublicEvent": ("PUBLIC", "#D9232E"),
    "WatchEvent": ("STAR", "#FFB4B4"),
    "ForkEvent": ("FORK", "#FF6B6B"),
    "PullRequestEvent": ("PR", "#D9232E"),
    "IssuesEvent": ("ISSUE", "#D9232E"),
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
.pulse{animation:pulse 2.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.rise{animation:rise .55s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(7px)}}
.sweep{animation:sweep 7.5s linear infinite}
@keyframes sweep{from{transform:translateX(-380px)}to{transform:translateX(1320px)}}
@media (prefers-reduced-motion:reduce){.pulse,.blink,.rise,.sweep{animation:none!important}}
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
        if len(rows) == 7:
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
    out.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#060A13"/><stop offset=".55" stop-color="#0A1120"/><stop offset="1" stop-color="#060A13"/></linearGradient>')
    out.append('<linearGradient id="scanline" x1="0" x2="1"><stop offset="0" stop-color="#6C9FE0" stop-opacity="0"/><stop offset=".5" stop-color="#6C9FE0" stop-opacity=".08"/><stop offset="1" stop-color="#6C9FE0" stop-opacity="0"/></linearGradient>')
    out.append('<radialGradient id="bloomBlue"><stop offset="0" stop-color="#D9232E" stop-opacity=".18"/><stop offset="1" stop-color="#D9232E" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="bloomCyan"><stop offset="0" stop-color="#6C9FE0" stop-opacity=".12"/><stop offset="1" stop-color="#6C9FE0" stop-opacity="0"/></radialGradient>')
    out.append('<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#1E2C48" stroke-opacity=".14"/></pattern>')
    out.append('<pattern id="scan" width="6" height="4" patternUnits="userSpaceOnUse"><rect width="6" height="1" fill="#000000" opacity=".14"/></pattern>')
    out.append(f'<clipPath id="win"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    out.append(f'<clipPath id="body"><rect x="0" y="{LOG_TOP}" width="{W}" height="{FOOTER - LOG_TOP}"/></clipPath>')
    out.append(f"<style>{CSS}</style>")
    out.append("</defs>")

    out.append('<g clip-path="url(#win)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    out.append('<ellipse cx="200" cy="140" rx="380" ry="260" fill="url(#bloomBlue)"/>')
    out.append('<ellipse cx="1080" cy="260" rx="380" ry="230" fill="url(#bloomCyan)"/>')
    out.append('<g fill="none" stroke="#F5F8FC" stroke-width="1" stroke-opacity=".05"><path d="M1280 0L1231 598M1280 0L1079 553M1280 0L943 477M1280 0L833 367M1280 0L757 231M1280 0L722 79"/><path d="M1280 180A180 180 0 0 1 1100 0M1280 320A320 320 0 0 1 960 0M1280 460A460 460 0 0 1 820 0M1280 600A600 600 0 0 1 680 0"/></g>')

    # window chrome
    out.append('<rect width="1280" height="46" fill="#0A1121" fill-opacity=".94"/><rect y="45" width="1280" height="1" fill="#1E2C48"/>')
    out.append('<circle cx="22" cy="23" r="5.5" fill="#D9232E" fill-opacity=".8" stroke="#D9232E"/><circle cx="40" cy="23" r="5.5" fill="#FFB4B4" fill-opacity=".8" stroke="#FFB4B4"/><circle cx="58" cy="23" r="5.5" fill="#6C9FE0" fill-opacity=".7" stroke="#6C9FE0"/>')
    out.append('<text class="m" x="640" y="28" text-anchor="middle" font-size="12" fill="#9BACC0">sujel@ewu: ~/activity.log — tail -f</text>')
    out.append('<rect x="1000" y="11" width="86" height="24" rx="12" fill="#D9232E" fill-opacity=".16" stroke="#D9232E" stroke-opacity=".8"/>')
    out.append('<circle class="pulse" cx="1018" cy="23" r="3" fill="#D9232E"/><text class="m" x="1027" y="27" font-size="9" letter-spacing="1.4" fill="#F5F8FC">LIVE</text>')
    out.append(f'<text class="m" x="1258" y="27" text-anchor="end" font-size="10.5" fill="#8FA1B6">{esc(stamp(now))}</text>')

    # tab strip
    out.append('<rect y="46" width="1280" height="42" fill="#080E1A" fill-opacity=".9"/><rect y="87" width="1280" height="1" fill="#1E2C48"/>')
    out.append('<rect x="20" y="53" width="116" height="25" rx="6" fill="#D9232E" fill-opacity=".14" stroke="#1E2C48" stroke-opacity=".65"/><rect x="20" y="76" width="116" height="2" fill="#FFB4B4"/>')
    out.append('<text class="m" x="78" y="70" text-anchor="middle" font-size="10.5" letter-spacing="1.4" fill="#F5F8FC">PUBLIC FEED</text>')
    out.append(f'<text class="m" x="156" y="70" font-size="10.5" letter-spacing="1.4" fill="#8FA1B6">EVENTS {len(rows):02d}</text>')
    out.append('<text class="m" x="252" y="70" font-size="10.5" letter-spacing="1.4" fill="#8FA1B6">RAW JSON</text>')
    out.append('<text class="m" x="1258" y="70" text-anchor="end" font-size="10" letter-spacing="1" fill="#6C9FE0">AUTO-SYNC · 3H</text>')

    # log lines
    out.append('<g clip-path="url(#body)">')
    for index, row in enumerate(rows):
        baseline = 120.0 + index * 29.0
        label, color = BADGES.get(row["type"], ("EVENT", "#8FA1B6"))
        tint = "#FFDADA" if color == "#D9232E" else color
        delay = 0.07 * index
        out.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">')
        if index == 0:
            out.append(f'<rect x="12" y="{baseline - 19:.1f}" width="1256" height="26" rx="6" fill="{color}" fill-opacity=".055"/>')
            out.append(f'<rect x="12" y="{baseline - 19:.1f}" width="2.5" height="26" rx="1.2" fill="{color}" fill-opacity=".8"/>')
        out.append(f'<text class="m" x="24" y="{baseline:.1f}" font-size="9.5" fill="#5C6D85">{index + 1:03d}</text>')
        try:
            moment = dt.datetime.fromisoformat(row["at"].replace("Z", "+00:00"))
            when = moment.strftime("%d %b · %H:%M").upper()
        except (ValueError, AttributeError):
            when = "—"
        out.append(f'<text class="m" x="58" y="{baseline:.1f}" font-size="11" fill="#8FA1B6">{when}</text>')
        badge_w = 74
        out.append(
            f'<rect x="170" y="{baseline - 13:.1f}" width="{badge_w}" height="19" rx="4" '
            f'fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".55"/>'
        )
        out.append(
            f'<text class="m" x="{170 + badge_w / 2:.1f}" y="{baseline - 0.5:.1f}" text-anchor="middle" '
            f'font-size="9.5" letter-spacing="1.1" fill="{tint}">{label}</text>'
        )
        out.append(
            f'<text class="m" x="262" y="{baseline:.1f}" font-size="12.5" fill="#E7EEF7">{esc(clip(row["text"], 84))}'
            f'<tspan fill="{tint}" fill-opacity=".9">  ·  {esc(clip(row["repo"], 40))}</tspan></text>'
        )
        out.append(f'<text class="m" x="1258" y="{baseline:.1f}" text-anchor="end" font-size="10" fill="#8FA1B6">{ago(row["at"])}</text>')
        out.append("</g>")
    out.append('<rect class="sweep" x="0" y="88" width="380" height="242" fill="url(#scanline)"/>')
    out.append("</g>")

    # prompt
    command = "tail -f activity.log"
    cursor_x = 128 + len(command) * 6.95 + 6
    out.append(f'<text class="m" x="24" y="{FOOTER - 18:.1f}" font-size="11.5" fill="#6C9FE0">sujel@ewu<tspan fill="#8FA1B6">:~$</tspan></text>')
    out.append(f'<text class="m" x="128" y="{FOOTER - 18:.1f}" font-size="11.5" fill="#B6C3D4">{command}</text>')
    out.append(f'<rect class="blink" x="{cursor_x:.1f}" y="{FOOTER - 28:.1f}" width="7" height="13" fill="#FFB4B4" fill-opacity=".85"/>')

    # footer
    out.append(f'<rect y="{FOOTER}" width="1280" height="42" fill="#080E1A" fill-opacity=".94"/><rect y="{FOOTER}" width="1280" height="1" fill="#1E2C48"/>')
    out.append(f'<text class="m" x="20" y="{FOOTER + 26}" font-size="10.5" fill="#8FA1B6">{len(rows)} events · public feed · last 30</text>')
    status = "CACHED SNAPSHOT" if cached else "STREAM OK"
    status_color = "#C08A1E" if cached else "#6C9FE0"
    out.append(f'<circle class="pulse" cx="356" cy="{FOOTER + 22}" r="3" fill="{status_color}"/>')
    out.append(f'<text class="m" x="366" y="{FOOTER + 26}" font-size="10.5" fill="{status_color}">{status}</text>')
    out.append(f'<text class="m" x="1260" y="{FOOTER + 26}" text-anchor="end" font-size="10.5" fill="#8FA1B6">github.com/{esc(USER)}</text>')

    out.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    out.append("</g>")
    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="#1E2C48" stroke-opacity=".45"/>')
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    target = REPO_ROOT / "assets" / "activity.svg"
    target.write_text(render(), encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
