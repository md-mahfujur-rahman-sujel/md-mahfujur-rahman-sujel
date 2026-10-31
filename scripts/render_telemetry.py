#!/usr/bin/env python3
"""Render the live contribution readout (assets/telemetry.svg)."""

from __future__ import annotations

import datetime as dt

from common import (
    LANG_COLORS,
    LANG_TEXT,
    PALETTE,
    REPO_ROOT,
    USER,
    build_weeks,
    contribution_stats,
    corner_web,
    esc,
    fetch_contributions,
    fetch_language_totals,
    fetch_repos,
    fetch_user,
    now_utc,
    short_date,
    spider,
    stamp,
)

W, H = 1280, 600
M = 56.0
CONTENT_W = W - M * 2
METRIC_X = (56.0, 344.0, 632.0, 920.0)
RULE_Y = 122.0
LANG_X, LANG_W = 56.0, 540.0
CHART_X, CHART_W = 656.0, 568.0
CHART_BASE, CHART_H = 470.0, 130.0

CSS = """
.s{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
.m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.grow{transform-box:fill-box;transform-origin:left center;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}}
.wv{transform-box:fill-box;transform-origin:center bottom;animation:wv .8s cubic-bezier(.2,.7,.2,1) both}
@keyframes wv{from{transform:scaleY(0)}}
.rise{animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@media (prefers-reduced-motion:reduce){.pulse,.grow,.wv,.rise{animation:none!important}}
"""


def metric(x: float, label: str, value: str, sub: str, color: str, delay: float) -> str:
    return (
        f'<g class="rise" style="animation-delay:{delay:.2f}s">'
        f'<text class="m" x="{x}" y="170" font-size="10.5" letter-spacing="2.2" fill="#8FA1B6">{label}</text>'
        f'<text class="s" x="{x}" y="230" font-size="56" font-weight="800" fill="{color}">{value}</text>'
        f'<text class="m" x="{x}" y="254" font-size="11.5" fill="#8FA1B6">{sub}</text>'
        "</g>"
    )


def week_month_labels(weeks: list[dict]) -> dict[int, str]:
    labels: dict[int, str] = {}
    labelled_months: set[str] = set()
    for index, week in enumerate(weeks):
        firsts = [
            dt.date.fromisoformat(day["date"])
            for day in week["days"]
            if dt.date.fromisoformat(day["date"]).day == 1
        ]
        if firsts:
            month = firsts[0].strftime("%b").upper()
            labels[index] = month
            labelled_months.add(month)
    if weeks:
        last_day = dt.date.fromisoformat(weeks[-1]["days"][-1]["date"])
        month = last_day.strftime("%b").upper()
        if month not in labelled_months:
            labels[len(weeks) - 1] = month
    return labels


def render() -> str:
    now = now_utc()
    user = fetch_user()
    repos = fetch_repos()
    languages = fetch_language_totals()
    days, total, cached = fetch_contributions()
    stats = contribution_stats(days, total)
    weeks = build_weeks(days, 53)

    cached = cached or not user or not repos
    def count(key: str, fallback: int) -> int:
        # A real 0 must stay 0; only a missing value (API unreachable) uses the fallback.
        value = user.get(key)
        return value if isinstance(value, int) else fallback

    public_repos = count("public_repos", len(repos) or 3)
    followers = count("followers", 1)
    following = count("following", 2)
    created = user.get("created_at", "2026-07-29T00:00:00Z")
    try:
        member_since = dt.date.fromisoformat(created[:10]).strftime("%b %Y").upper()
    except ValueError:
        member_since = "JUL 2026"

    if not languages:
        languages = [
            ("HTML", 812197),
            ("TypeScript", 473923),
            ("JavaScript", 414700),
            ("Kotlin", 193864),
        ]
        cached = True
    total_bytes = sum(size for _, size in languages) or 1
    top_languages = languages[:4]
    lang_colors = [PALETTE[0], PALETTE[4], PALETTE[3], PALETTE[2]]
    lang_text_colors = ["#FFC9C9", "#6C9FE0", "#FFB4B4", "#FFDADA"]

    totals = [week["total"] for week in weeks] or [0]
    peak_week = max(totals) if totals else 0
    week_max = peak_week or 1
    bar_gap = 3.0
    bar_w = (CHART_W - (len(totals) - 1) * bar_gap) / len(totals)
    month_labels = week_month_labels(weeks)
    window_days = len(days) or 365
    consistency = (stats["active_days"] / window_days) * 100

    current_sub = (
        f"{short_date(stats['current_start'])} → {short_date(stats['current_end'])}"
        if stats["current"]
        else "NO ACTIVE STREAK"
    )
    longest_sub = (
        f"{short_date(stats['longest_start'])} → {short_date(stats['longest_end'])}"
        if stats["longest"]
        else "NO STREAK YET"
    )

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Live GitHub contributions for {esc(user.get("name") or USER)}: '
        f'{stats["total"]} contributions, {stats["current"]}-day current streak, '
        f'{stats["active_days"]} active days">'
    )
    out.append("<defs>")
    out.append('<linearGradient id="bg" x1="0" y1="0" x2=".85" y2="1"><stop offset="0" stop-color="#070C16"/><stop offset=".55" stop-color="#0A1223"/><stop offset="1" stop-color="#060A13"/></linearGradient>')
    out.append('<radialGradient id="glowRed"><stop offset="0" stop-color="#D9232E" stop-opacity=".18"/><stop offset="1" stop-color="#D9232E" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="glowBlue"><stop offset="0" stop-color="#6C9FE0" stop-opacity=".12"/><stop offset="1" stop-color="#6C9FE0" stop-opacity="0"/></radialGradient>')
    out.append('<linearGradient id="barRamp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9232E"/><stop offset="1" stop-color="#FF6B6B"/></linearGradient>')
    out.append(f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>')
    out.append(f'<clipPath id="chart"><rect x="{CHART_X}" y="{CHART_BASE - CHART_H}" width="{CHART_W}" height="{CHART_H}"/></clipPath>')
    out.append(f"<style>{CSS}</style>")
    out.append("</defs>")

    out.append('<g clip-path="url(#frame)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append('<ellipse cx="80" cy="600" rx="520" ry="320" fill="url(#glowRed)"/>')
    out.append('<ellipse cx="1240" cy="20" rx="380" ry="260" fill="url(#glowBlue)"/>')
    out.append(corner_web(1288, 22, 205, spokes=9, rings=(0.42, 0.72, 1.0), rotation=2.2, opacity=0.13, width=1.5))
    out.append(spider(704, 64, 1.05, thread=64, opacity=0.55))

    # masthead
    out.append('<g class="rise">')
    out.append(f'<circle class="pulse" cx="62" cy="48" r="3.5" fill="#D9232E"/>')
    out.append('<text class="m" x="78" y="52" font-size="11" letter-spacing="2.6" fill="#FF9A9A">LIVE · SPIDER-SENSE</text>')
    out.append(f'<text class="m" x="1224" y="52" text-anchor="end" font-size="10.5" fill="#8FA1B6">{esc(stamp(now))}</text>')
    out.append('<text class="s" x="56" y="102" font-size="32" font-weight="800" letter-spacing="-.4" fill="#F5F8FC">Contribution pulse</text>')
    out.append(f'<rect x="{M}" y="{RULE_Y}" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".8"/>')
    out.append("</g>")

    # four headline numerals
    out.append(metric(METRIC_X[0], "CONTRIBUTIONS", str(stats["total"]), "LAST 12 MONTHS", "#F5F8FC", 0.05))
    out.append(metric(METRIC_X[1], "CURRENT STREAK", str(stats["current"]), current_sub, "#FF6B6B", 0.12))
    out.append(metric(METRIC_X[2], "LONGEST STREAK", str(stats["longest"]), longest_sub, "#F5F8FC", 0.19))
    out.append(metric(METRIC_X[3], "ACTIVE DAYS", str(stats["active_days"]), f"OF {window_days} · {consistency:.1f}% CONSISTENT", "#6C9FE0", 0.26))
    for x in (328.0, 616.0, 904.0):
        out.append(f'<rect x="{x}" y="146" width="1" height="118" fill="#1E2C48" fill-opacity=".55"/>')

    # languages
    out.append('<g class="rise" style="animation-delay:.32s">')
    out.append(f'<text class="m" x="{LANG_X}" y="306" font-size="10.5" letter-spacing="2.2" fill="#8FA1B6">BYTES BY LANGUAGE</text>')
    out.append(f'<text class="m" x="{LANG_X + LANG_W}" y="306" text-anchor="end" font-size="10.5" fill="#6D7E94">{total_bytes / 1_000_000:.1f} MB · OWN REPOS</text>')
    if top_languages:
        for index, (name, size) in enumerate(top_languages):
            pct = size / total_bytes * 100
            color = LANG_COLORS.get(name) or lang_colors[index % len(lang_colors)]
            text_color = LANG_TEXT.get(name) or lang_text_colors[index % len(lang_text_colors)]
            baseline = 340 + index * 36
            out.append(f'<text class="s" x="{LANG_X}" y="{baseline}" font-size="15" fill="#E7EEF7">{esc(name)}</text>')
            out.append(f'<text class="m" x="{LANG_X + LANG_W}" y="{baseline}" text-anchor="end" font-size="12" fill="{text_color}">{pct:.1f}%</text>')
            out.append(f'<rect x="{LANG_X}" y="{baseline + 10}" width="{LANG_W}" height="4" rx="2" fill="#101A2E"/>')
            out.append(
                f'<rect class="grow" x="{LANG_X}" y="{baseline + 10}" width="{LANG_W * pct / 100:.1f}" height="4" '
                f'rx="2" fill="{color}" style="animation-delay:{0.08 * index:.2f}s"/>'
            )
    out.append("</g>")

    # weekly chart
    out.append('<g class="rise" style="animation-delay:.38s">')
    out.append(f'<text class="m" x="{CHART_X}" y="306" font-size="10.5" letter-spacing="2.2" fill="#8FA1B6">52-WEEK ACTIVITY</text>')
    out.append(
        f'<text class="m" x="{CHART_X + CHART_W}" y="306" text-anchor="end" font-size="10.5" fill="#8FA1B6">'
        f'PEAK <tspan fill="#FFB4B4">{stats["peak"]:02d}</tspan> · {short_date(stats["peak_date"])}</text>'
    )
    out.append(f'<rect x="{CHART_X}" y="{CHART_BASE}" width="{CHART_W}" height="1" fill="#1E2C48" fill-opacity=".8"/>')
    out.append(f'<rect x="{CHART_X}" y="{CHART_BASE - CHART_H / 2:.0f}" width="{CHART_W}" height="1" fill="#1E2C48" fill-opacity=".3"/>')

    peak_index = -1
    for index, week in enumerate(weeks):
        bar_h = (4 + (week["total"] / week_max) * CHART_H) if week["total"] else 4
        bar_x = CHART_X + index * (bar_w + bar_gap)
        bar_y = CHART_BASE - bar_h
        ratio = week["total"] / week_max if week_max else 0
        if week["total"] == 0:
            color = "#101A2E"
        elif ratio <= 0.25:
            color = "#1E2C48"
        elif ratio <= 0.5:
            color = "#FF6B6B"
        elif ratio <= 0.75:
            color = "#FFB4B4"
        else:
            color = "#FFC857"
        if week["total"] == peak_week and week["total"] > 0:
            peak_index = index
        out.append(
            f'<rect class="wv" x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'rx="1.4" fill="{color}" style="animation-delay:{index * 0.012:.2f}s"/>'
        )
        label = month_labels.get(index)
        if label:
            label_x = min(max(bar_x + bar_w / 2, CHART_X + 10), CHART_X + CHART_W - 10)
            out.append(
                f'<text class="m" x="{label_x:.1f}" y="488" text-anchor="middle" font-size="9.5" '
                f'letter-spacing=".6" fill="#8FA1B6">{label}</text>'
            )
    if peak_index >= 0:
        px = CHART_X + peak_index * (bar_w + bar_gap) + bar_w / 2
        out.append(f'<circle class="pulse" cx="{px:.1f}" cy="{CHART_BASE - CHART_H - 12:.1f}" r="3.2" fill="#FFC857"/>')
    out.append("</g>")

    # footer line
    status = "CACHED SNAPSHOT" if cached else "SYNC OK"
    status_color = "#C08A1E" if cached else "#6C9FE0"
    out.append(f'<rect x="{M}" y="520" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".7"/>')
    out.append(f'<text class="m" x="56" y="550" font-size="11" fill="#8FA1B6">{public_repos} public repos · {followers} followers · {following} following · member since {member_since}</text>')
    out.append(f'<circle class="pulse" cx="760" cy="546" r="3" fill="{status_color}"/>')
    out.append(f'<text class="m" x="772" y="550" font-size="11" fill="{status_color}">{status}</text>')
    out.append(f'<text class="m" x="1224" y="550" text-anchor="end" font-size="11" fill="#6D7E94">github.com/{esc(USER)}</text>')

    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#1E2C48" stroke-opacity=".4"/>')
    out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    target = REPO_ROOT / "assets" / "telemetry.svg"
    target.write_text(render(), encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
