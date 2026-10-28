#!/usr/bin/env python3
"""Render the live telemetry dashboard (assets/telemetry.svg)."""

from __future__ import annotations

import datetime as dt
import math

from common import (
    LANG_COLORS,
    LANG_TEXT,
    PALETTE,
    REPO_ROOT,
    USER,
    build_weeks,
    contribution_stats,
    esc,
    fetch_contributions,
    fetch_language_totals,
    fetch_repos,
    fetch_user,
    now_utc,
    short_date,
    stamp,
)

W, H = 1280, 680
PAD = 20.0
GAP = 16.0
COL_W = (W - PAD * 2 - GAP * 2) / 3
COLS = [PAD, PAD + COL_W + GAP, PAD + (COL_W + GAP) * 2]
ROW1 = (104.0, 196.0)
ROW2 = (316.0, 104.0)
ROW3 = (436.0, 168.0)
CHART_X, CHART_W = 40.0, 1200.0
CHART_BASE, CHART_H = 566.0, 74.0

CSS = """
.s{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
.m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.pulse{animation:pulse 2.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.grow{transform-box:fill-box;transform-origin:left center;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}}
.wv{transform-box:fill-box;transform-origin:center bottom;animation:wv .8s cubic-bezier(.2,.7,.2,1) both}
@keyframes wv{from{transform:scaleY(0)}}
.rise{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(8px)}}
.scanA{animation:scanA 9s linear infinite}
@keyframes scanA{from{transform:translateX(0)}to{transform:translateX(1420px)}}
.scanB{animation:scanB 11s linear infinite}
@keyframes scanB{from{transform:translateX(0)}to{transform:translateX(1460px)}}
@media (prefers-reduced-motion:reduce){.pulse,.blink,.grow,.wv,.rise,.scanA,.scanB{animation:none!important}}
"""


def panel(x: float, y: float, w: float, h: float, accent: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#glass)" stroke="#16263A" stroke-opacity=".55"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="2.5" rx="1.2" fill="{accent}" fill-opacity=".92"/>'
    )


def card_header(x: float, y: float, w: float, color: str, title: str, right: str) -> str:
    return (
        f'<circle cx="{x + 23}" cy="{y + 23}" r="4" fill="{color}"/>'
        f'<circle cx="{x + 23}" cy="{y + 23}" r="8" fill="{color}" fill-opacity=".12"/>'
        f'<text class="m" x="{x + 38}" y="{y + 27}" font-size="11.5" letter-spacing="2" fill="#9FB2C6">{title}</text>'
        f'<text class="m" x="{x + w - 18}" y="{y + 27}" text-anchor="end" font-size="10.5" letter-spacing="1" fill="#7E93A8">{right}</text>'
        f'<rect x="{x + 18}" y="{y + 40}" width="{w - 36}" height="1" fill="#16263A" opacity=".55"/>'
    )


def stat_tile(x: float, y: float, w: float, h: float, label: str, value: str, color: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#080D13" stroke="#16263A" stroke-opacity=".6"/>'
        f'<rect x="{x}" y="{y}" width="2.5" height="{h - 16}" rx="1.2" fill="{color}" transform="translate(0 8)"/>'
        f'<text class="m" x="{x + 14}" y="{y + 19}" font-size="10" letter-spacing="1.3" fill="#7E93A8">{label}</text>'
        f'<text class="s" x="{x + 14}" y="{y + 43}" font-size="24" font-weight="800" fill="#EEF6FF">{value}</text>'
        f'<circle cx="{x + w - 14}" cy="{y + 15}" r="2.5" fill="{color}" opacity=".8"/>'
    )


def streak_tile(
    x: float,
    w: float,
    label: str,
    value: int,
    sub: str,
    accent: str,
    spark: list[int],
) -> str:
    y, h = ROW2
    bars = []
    peak = max(spark) or 1
    start_x = x + w - 130
    for index, count in enumerate(spark[-14:]):
        bar_h = 2 + (count / peak) * 22 if count else 2
        bar_x = start_x + index * 8
        fill = accent if count else "#182434"
        opacity = ".95" if count else "1"
        bars.append(
            f'<rect x="{bar_x:.1f}" y="{392 - bar_h:.1f}" width="5" height="{bar_h:.1f}" rx="1.5" fill="{fill}" opacity="{opacity}"/>'
        )
    value_text = f"{value:02d}"
    # 42px bold digits advance ~23.5px; anchor DAYS after the numeral so a
    # 3-digit streak does not collide with it.
    days_x = x + 18 + len(value_text) * 23.5 + 6
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="13" fill="url(#glassSoft)" stroke="#16263A" stroke-opacity=".55"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="2.5" rx="1.2" fill="{accent}" fill-opacity=".9"/>'
        f'<text class="m" x="{x + 18}" y="{y + 24}" font-size="10.5" letter-spacing="1.8" fill="#7E93A8">{label}</text>'
        f'<text class="s" x="{x + 18}" y="{y + 68}" font-size="42" font-weight="800" fill="#EEF6FF">{value_text}</text>'
        f'<text class="m" x="{days_x:.1f}" y="{y + 66}" font-size="10.5" letter-spacing="1.5" fill="{accent}">DAYS</text>'
        f'<text class="m" x="{x + 18}" y="{y + 88}" font-size="10.5" fill="#7E93A8">{sub}</text>'
        + "".join(bars)
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
    stars = sum(int(repo.get("stargazers_count") or 0) for repo in repos)
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
    lang_text_colors = ["#93C5FD", "#67C7EB", "#A9C7FF", "#BFDBFE"]

    today = now.date()
    year_start = dt.date(today.year, 1, 1)
    year_pct = ((today - year_start).days + 1) / ((dt.date(today.year + 1, 1, 1) - year_start).days)
    ring_r = 52.0
    ring_c = 2 * math.pi * ring_r
    ring_len = ring_c * year_pct
    ring_angle = -90 + 360 * year_pct
    dot_x = 640 + ring_r * math.cos(math.radians(ring_angle))
    dot_y = 206 + ring_r * math.sin(math.radians(ring_angle))

    totals = [week["total"] for week in weeks] or [0]
    peak_week = max(totals) if totals else 0
    week_max = peak_week or 1
    bar_gap = 4.5
    bar_w = (CHART_W - (len(totals) - 1) * bar_gap) / len(totals)
    month_labels = week_month_labels(weeks)
    last14 = [row["count"] for row in sorted(days, key=lambda row: row["date"])[-14:]]
    while len(last14) < 14:
        last14.insert(0, 0)
    window_days = len(days) or 365

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
    consistency = (stats["active_days"] / window_days) * 100

    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Live GitHub telemetry for {esc(user.get("name") or USER)}: {stats["total"]} contributions, {stats["current"]}-day current streak, {stats["active_days"]} active days">')
    out.append("<defs>")
    out.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05080D"/><stop offset=".55" stop-color="#090F16"/><stop offset="1" stop-color="#05080D"/></linearGradient>')
    out.append('<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16263A" stop-opacity=".26"/><stop offset=".55" stop-color="#141F2C" stop-opacity=".55"/><stop offset="1" stop-color="#67C7EB" stop-opacity=".05"/></linearGradient>')
    out.append('<linearGradient id="glassSoft" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16263A" stop-opacity=".16"/><stop offset="1" stop-color="#67C7EB" stop-opacity=".04"/></linearGradient>')
    out.append('<linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3B82F6"/><stop offset=".55" stop-color="#A9C7FF"/><stop offset="1" stop-color="#67C7EB"/></linearGradient>')
    out.append('<linearGradient id="scanline" x1="0" x2="1"><stop offset="0" stop-color="#67C7EB" stop-opacity="0"/><stop offset=".5" stop-color="#67C7EB" stop-opacity=".12"/><stop offset="1" stop-color="#67C7EB" stop-opacity="0"/></linearGradient>')
    out.append('<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="#05080D"/><stop offset="1" stop-color="#05080D" stop-opacity="0"/></linearGradient>')
    out.append('<radialGradient id="bloomBlue"><stop offset="0" stop-color="#3B82F6" stop-opacity=".22"/><stop offset="1" stop-color="#3B82F6" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="bloomMid"><stop offset="0" stop-color="#4F8DFF" stop-opacity=".16"/><stop offset="1" stop-color="#4F8DFF" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="bloomCyan"><stop offset="0" stop-color="#67C7EB" stop-opacity=".14"/><stop offset="1" stop-color="#67C7EB" stop-opacity="0"/></radialGradient>')
    out.append('<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#16263A" stroke-opacity=".16"/></pattern>')
    out.append('<pattern id="scan" width="6" height="4" patternUnits="userSpaceOnUse"><rect width="6" height="1" fill="#000000" opacity=".14"/></pattern>')
    out.append('<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    out.append(f'<clipPath id="win"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    out.append(f'<clipPath id="chart"><rect x="{CHART_X}" y="484" width="{CHART_W}" height="92"/></clipPath>')
    out.append(f"<style>{CSS}</style>")
    out.append("</defs>")

    out.append('<g clip-path="url(#win)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    out.append('<ellipse cx="210" cy="90" rx="420" ry="280" fill="url(#bloomBlue)"/>')
    out.append('<ellipse cx="760" cy="380" rx="430" ry="280" fill="url(#bloomMid)"/>')
    out.append('<ellipse cx="1180" cy="170" rx="330" ry="260" fill="url(#bloomCyan)"/>')

    # window chrome
    out.append('<rect width="1280" height="46" fill="#080E15" fill-opacity=".94"/><rect y="45" width="1280" height="1" fill="#16263A"/>')
    out.append('<circle cx="22" cy="23" r="5.5" fill="#3B82F6" fill-opacity=".8" stroke="#3B82F6"/><circle cx="40" cy="23" r="5.5" fill="#A9C7FF" fill-opacity=".8" stroke="#A9C7FF"/><circle cx="58" cy="23" r="5.5" fill="#67C7EB" fill-opacity=".7" stroke="#67C7EB"/>')
    out.append('<text class="m" x="640" y="28" text-anchor="middle" font-size="12" fill="#8EA1B5">sujel@ewu: ~/telemetry --live</text>')
    out.append('<rect x="1000" y="11" width="86" height="24" rx="12" fill="#3B82F6" fill-opacity=".16" stroke="#3B82F6" stroke-opacity=".8"/>')
    out.append('<circle class="pulse" cx="1018" cy="23" r="3" fill="#3B82F6"/><text class="m" x="1027" y="27" font-size="9" letter-spacing="1.4" fill="#EEF6FF">LIVE</text>')
    out.append(f'<text class="m" x="1258" y="27" text-anchor="end" font-size="10.5" fill="#7E93A8">{esc(stamp(now))}</text>')

    # tab strip
    out.append('<rect y="46" width="1280" height="42" fill="#070C12" fill-opacity=".9"/><rect y="87" width="1280" height="1" fill="#16263A"/>')
    out.append('<rect x="20" y="53" width="92" height="25" rx="6" fill="#3B82F6" fill-opacity=".14" stroke="#16263A" stroke-opacity=".65"/><rect x="20" y="76" width="92" height="2" fill="#A9C7FF"/>')
    out.append('<text class="m" x="32" y="70" font-size="10.5" letter-spacing="1.4" fill="#EEF6FF">OVERVIEW</text>')
    out.append('<text class="m" x="128" y="70" font-size="10.5" letter-spacing="1.4" fill="#7E93A8">STREAKS</text>')
    out.append('<text class="m" x="206" y="70" font-size="10.5" letter-spacing="1.4" fill="#7E93A8">LANGUAGES</text>')
    out.append('<text class="m" x="1258" y="70" text-anchor="end" font-size="10" letter-spacing="1" fill="#67C7EB">SYS.OK · 60 FPS</text>')

    # column 1 — node status
    x, y, w, h = COLS[0], ROW1[0], COL_W, ROW1[1]
    out.append(panel(x, y, w, h, "#A9C7FF"))
    out.append(card_header(x, y, w, "#A9C7FF", "NODE STATUS", "01"))
    tile_w = (w - 36 - 10) / 2
    for index, (label, value, color) in enumerate(
        [
            ("REPOSITORIES", f"{public_repos:02d}", "#A9C7FF"),
            ("STARS", f"{stars:02d}", "#4F8DFF"),
            ("FOLLOWERS", f"{followers:02d}", "#67C7EB"),
            ("FOLLOWING", f"{following:02d}", "#3B82F6"),
        ]
    ):
        tx = x + 18 + (index % 2) * (tile_w + 10)
        ty = y + 48 + (index // 2) * 62
        out.append(stat_tile(tx, ty, tile_w, 54, label, value, color))
    out.append(f'<text class="m" x="{x + 18}" y="{y + 186}" font-size="10" letter-spacing="1.2" fill="#7E93A8">MEMBER SINCE {member_since}</text>')
    out.append(f'<circle class="pulse" cx="{x + w - 54}" cy="{y + 183}" r="3" fill="#67C7EB"/>')
    out.append(f'<text class="m" x="{x + w - 18}" y="{y + 186}" text-anchor="end" font-size="10" letter-spacing="1.2" fill="#67C7EB">SYS.OK</text>')

    # column 2 — contributions ring
    x = COLS[1]
    out.append(panel(x, y, w, h, "#3B82F6"))
    out.append(card_header(x, y, w, "#3B82F6", "CONTRIBUTIONS", "12M"))
    out.append('<circle cx="640" cy="206" r="52" fill="#080E15" stroke="#182434" stroke-width="10"/>')
    out.append(f'<circle cx="640" cy="206" r="52" fill="none" stroke="url(#ringGrad)" stroke-width="10" stroke-linecap="round" stroke-dasharray="{ring_len:.1f} {ring_c:.1f}" transform="rotate(-90 640 206)"/>')
    out.append(f'<circle cx="{dot_x:.1f}" cy="{dot_y:.1f}" r="5" fill="#A9C7FF" stroke="#05080D" stroke-width="2" filter="url(#glow)"/>')
    out.append(f'<circle class="pulse" cx="{dot_x:.1f}" cy="{dot_y:.1f}" r="9" fill="none" stroke="#A9C7FF" stroke-opacity=".5"/>')
    total_digits = len(str(stats["total"]))
    total_size = 44 if total_digits <= 3 else 36 if total_digits == 4 else 30
    out.append(f'<text class="s" x="640" y="214" text-anchor="middle" font-size="{total_size}" font-weight="800" fill="#A9C7FF">{stats["total"]}</text>')
    out.append('<text class="m" x="640" y="232" text-anchor="middle" font-size="9" letter-spacing=".3" fill="#7E93A8">LAST 12 MONTHS</text>')
    out.append(f'<text class="m" x="640" y="274" text-anchor="middle" font-size="10" letter-spacing="1" fill="#4F8DFF">{today.year} · {year_pct * 100:.0f}% ELAPSED</text>')
    out.append(f'<text class="m" x="{x + 18}" y="{y + 190}" font-size="10.5" fill="#7E93A8">ACTIVE <tspan fill="#67C7EB">{stats["active_days"]:02d}</tspan></text>')
    out.append(f'<text class="m" x="{x + w - 18}" y="{y + 190}" text-anchor="end" font-size="10.5" fill="#7E93A8">PEAK <tspan fill="#A9C7FF">{stats["peak"]:02d}</tspan></text>')

    # column 3 — languages
    x = COLS[2]
    out.append(panel(x, y, w, h, "#67C7EB"))
    out.append(card_header(x, y, w, "#67C7EB", "LANGUAGES", "BY BYTES"))
    if top_languages:
        for index, (name, size) in enumerate(top_languages):
            pct = size / total_bytes * 100
            color = LANG_COLORS.get(name) or lang_colors[index % len(lang_colors)]
            text_color = LANG_TEXT.get(name) or lang_text_colors[index % len(lang_text_colors)]
            row_y = y + 52 + index * 34
            bar_width = (w - 36) * pct / 100
            out.append(f'<text class="s" x="{x + 18}" y="{row_y + 10}" font-size="14" fill="#EEF6FF">{esc(name)}</text>')
            out.append(f'<text class="m" x="{x + w - 18}" y="{row_y + 10}" text-anchor="end" font-size="12" fill="{text_color}">{pct:.1f}%</text>')
            out.append(f'<rect x="{x + 18}" y="{row_y + 17}" width="{w - 36}" height="5" rx="2.5" fill="#111B27"/>')
            out.append(f'<rect class="grow" x="{x + 18}" y="{row_y + 17}" width="{bar_width:.1f}" height="5" rx="2.5" fill="{color}" style="animation-delay:{0.08 * index:.2f}s"/>')
    else:
        out.append(f'<text class="m" x="{640}" y="205" text-anchor="middle" font-size="10" fill="#7E93A8">NO LANGUAGE DATA</text>')
    out.append(f'<text class="m" x="{x + 18}" y="{y + 186}" font-size="10" letter-spacing="1.2" fill="#7E93A8">BYTES · OWN REPOS</text>')
    out.append(f'<text class="m" x="{x + w - 18}" y="{y + 186}" text-anchor="end" font-size="10" fill="#67C7EB">{total_bytes / 1_000_000:.1f} MB</text>')

    # row 2 — streak KPIs
    out.append(streak_tile(COLS[0], COL_W, "CURRENT STREAK", stats["current"], current_sub, "#A9C7FF", last14))
    out.append(streak_tile(COLS[1], COL_W, "LONGEST STREAK", stats["longest"], longest_sub, "#4F8DFF", last14))
    out.append(
        streak_tile(
            COLS[2],
            COL_W,
            "ACTIVE DAYS",
            stats["active_days"],
            f"OF {window_days} · {consistency:.1f}% CONSISTENCY",
            "#67C7EB",
            last14,
        )
    )

    # row 3 — activity carrier
    x, y, w, h = PAD, ROW3[0], W - PAD * 2, ROW3[1]
    out.append(panel(x, y, w, h, "#A9C7FF"))
    out.append(f'<text class="m" x="{x + 20}" y="{y + 25}" font-size="11.5" letter-spacing="2" fill="#9FB2C6">ACTIVITY CARRIER</text>')
    out.append(f'<text class="m" x="{x + 170}" y="{y + 25}" font-size="10.5" fill="#7E93A8">52 WEEK WINDOW</text>')
    out.append(f'<text class="m" x="{x + w - 20}" y="{y + 25}" text-anchor="end" font-size="10.5" fill="#7E93A8">PEAK <tspan fill="#A9C7FF">{stats["peak"]:02d}</tspan> · {short_date(stats["peak_date"])}</text>')
    out.append(f'<rect x="{CHART_X}" y="484" width="{CHART_W}" height="1" fill="#16263A" opacity=".35"/>')
    out.append(f'<rect x="{CHART_X}" y="500" width="{CHART_W}" height="1" fill="#16263A" opacity=".22"/>')
    out.append(f'<rect x="{CHART_X}" y="530" width="{CHART_W}" height="1" fill="#16263A" opacity=".22"/>')
    out.append(f'<rect x="{CHART_X}" y="{CHART_BASE}" width="{CHART_W}" height="1" fill="#16263A" opacity=".8"/>')

    points = []
    peak_index = -1
    for index, week in enumerate(weeks):
        bar_h = (3 + (week["total"] / week_max) * CHART_H) if week["total"] else 3
        bar_x = CHART_X + index * (bar_w + bar_gap)
        bar_y = CHART_BASE - bar_h
        ratio = week["total"] / week_max if week_max else 0
        if week["total"] == 0:
            color = "#111B27"
        elif ratio <= 0.25:
            color = "#16263A"
        elif ratio <= 0.5:
            color = "#4F8DFF"
        elif ratio <= 0.75:
            color = "#A9C7FF"
        else:
            color = "#FBCA03"
        if week["total"] == peak_week and week["total"] > 0:
            peak_index = index
        out.append(
            f'<rect class="wv" x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="1.6" fill="{color}" style="animation-delay:{index * 0.012:.2f}s"/>'
        )
        points.append(f"{bar_x + bar_w / 2:.1f},{bar_y:.1f}")

        label = month_labels.get(index)
        if label:
            label_x = min(max(bar_x + bar_w / 2, CHART_X + 10), CHART_X + CHART_W - 10)
            out.append(f'<text class="m" x="{label_x:.1f}" y="478" text-anchor="middle" font-size="9.5" letter-spacing=".4" fill="#7E93A8">{label}</text>')

    if len(points) > 1:
        out.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#67C7EB" stroke-opacity=".32" stroke-width="1.2"/>')
    if peak_index >= 0:
        px = CHART_X + peak_index * (bar_w + bar_gap) + bar_w / 2
        py = CHART_BASE - (3 + (peak_week / week_max) * CHART_H)
        out.append(f'<circle class="pulse" cx="{px:.1f}" cy="{py - 7:.1f}" r="3.2" fill="#FBCA03" filter="url(#glow)"/>')
        out.append(f'<text class="m" x="{px:.1f}" y="{py - 14:.1f}" text-anchor="middle" font-size="9.5" fill="#FBCA03">{stats["peak"]}</text>')

    out.append('<rect class="scanA" x="-140" y="484" width="140" height="92" fill="url(#scanline)"/>')

    # footer
    out.append('<rect y="620" width="1280" height="60" fill="#070C12" fill-opacity=".94"/><rect y="620" width="1280" height="1" fill="#16263A"/>')
    out.append(f'<text class="m" x="20" y="654" font-size="11.5" fill="#7E93A8">{stats["total"]} contributions · {stats["active_days"]} active days · {window_days}d window</text>')
    status = "CACHED SNAPSHOT" if cached else "SYNC OK"
    status_color = "#B97D10" if cached else "#67C7EB"
    out.append(f'<circle class="pulse" cx="600" cy="650" r="3" fill="{status_color}"/>')
    out.append(f'<text class="m" x="610" y="654" font-size="11" fill="{status_color}">{status}</text>')
    stamp_x = 610 + len(status) * 6.6 + 18
    out.append(f'<text class="m" x="{stamp_x:.1f}" y="654" font-size="11" fill="#7E93A8">· {esc(stamp(now))}</text>')
    out.append(f'<text class="m" x="1260" y="654" text-anchor="end" font-size="11.5" fill="#7E93A8">github.com/{esc(USER)}</text>')

    out.append('<rect class="scanB" x="-180" y="46" width="180" height="574" fill="url(#scanline)"/>')
    out.append('<rect width="1280" height="680" fill="url(#scan)"/>')
    out.append("</g>")
    out.append('<rect x=".5" y=".5" width="1279" height="679" rx="20" fill="none" stroke="#16263A" stroke-opacity=".45"/>')
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    target = REPO_ROOT / "assets" / "telemetry.svg"
    target.write_text(render(), encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
