#!/usr/bin/env python3
"""Render the live repository index (assets/repos.svg)."""

from __future__ import annotations

from common import (
    LANG_COLORS,
    REPO_ROOT,
    USER,
    clip,
    corner_web,
    esc,
    fetch_repo,
    now_utc,
    relative_day,
    spider,
    stamp,
)

W, H = 1280, 480
M = 56.0
CONTENT_W = W - M * 2
ROW_TOP = 146.0
ROW_H = 92.0
ROWS = 3

REPOS = [
    {
        "full": "md-mahfujur-rahman-sujel/Apex-Arcade",
        "name": "Apex Arcade",
        "accent": "#FF6B6B",
        "kind": "web",
        "fallback_desc": "React launcher for 50 browser games with history, favorites and score cards.",
        "fallback_lang": "HTML",
    },
    {
        "full": "md-mahfujur-rahman-sujel/Unrot",
        "name": "Unrot",
        "accent": "#6C9FE0",
        "kind": "android",
        "fallback_desc": "Locks distracting apps behind a focus timer; earn time back with math challenges.",
        "fallback_lang": "Kotlin",
    },
    {
        "full": "masum-mir/Oppzy",
        "name": "Oppzy",
        "accent": "#FFC857",
        "kind": "web",
        "fallback_desc": "Internship and research matching platform, built as a team project with Spring Boot.",
        "fallback_lang": "JavaScript",
    },
]

CSS = """
.s{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
.m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.rise{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@media (prefers-reduced-motion:reduce){.pulse,.rise{animation:none!important}}
"""


def rows() -> list[dict]:
    output = []
    for repo in REPOS:
        data = fetch_repo(repo["full"])
        owner = repo["full"].split("/", 1)[0]
        output.append(
            {
                **repo,
                "owner": owner,
                "language": data.get("language") or repo["fallback_lang"],
                "description": data.get("description") or repo["fallback_desc"],
                "stars": int(data.get("stargazers_count") or 0),
                "forks": int(data.get("forks_count") or 0),
                "updated": relative_day(data.get("pushed_at")),
                "live": bool(data),
            }
        )
    return output


def render() -> str:
    now = now_utc()
    repos = rows()
    cached = not all(repo["live"] for repo in repos)
    owned = sum(1 for repo in repos if repo["owner"] == USER)
    collab = len(repos) - owned
    languages = {repo["language"] for repo in repos}

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Repository index for {esc(USER)}: {", ".join(repo["name"] for repo in repos)}">'
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
    out.append('<ellipse cx="60" cy="0" rx="460" ry="280" fill="url(#glowRed)"/>')
    out.append('<ellipse cx="1240" cy="470" rx="420" ry="280" fill="url(#glowBlue)"/>')
    out.append(corner_web(1288, 22, 205, spokes=9, rings=(0.42, 0.72, 1.0), rotation=2.2, opacity=0.13, width=1.5))
    out.append(spider(762, 62, 1.0, thread=62, opacity=0.5))

    out.append('<g class="rise">')
    out.append('<circle class="pulse" cx="62" cy="48" r="3.5" fill="#D9232E"/>')
    out.append('<text class="m" x="78" y="52" font-size="11" letter-spacing="2.6" fill="#FF9A9A">REPOSITORIES · LIVE</text>')
    out.append('<text class="s" x="56" y="106" font-size="32" font-weight="800" letter-spacing="-.4" fill="#F5F8FC">Case files</text>')
    out.append(
        f'<text class="m" x="1224" y="52" text-anchor="end" font-size="10.5" fill="#8FA1B6">'
        f'{len(repos):02d} PUBLIC · {owned:02d} OWNED · {collab:02d} COLLAB · {len(languages):02d} LANGUAGES</text>'
    )
    out.append(f'<text class="m" x="1224" y="106" text-anchor="end" font-size="10.5" fill="#6D7E94">{esc(stamp(now))}</text>')
    out.append(f'<rect x="{M}" y="124" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".8"/>')
    out.append("</g>")

    for index, repo in enumerate(repos):
        y = ROW_TOP + index * ROW_H
        accent = repo["accent"]
        lang_color = LANG_COLORS.get(repo["language"], accent)
        updated = "PENDING" if repo["updated"] == "—" else repo["updated"].upper()
        ownership = "OWNED" if repo["owner"] == USER else "COLLABORATOR"
        out.append(f'<g class="rise" style="animation-delay:{0.06 + 0.08 * index:.2f}s">')
        if index:
            out.append(f'<rect x="{M}" y="{y - 2:.1f}" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".55"/>')
        out.append(f'<rect x="{M}" y="{y + 18:.1f}" width="3" height="46" rx="1.5" fill="{accent}"/>')
        out.append(f'<text class="s" x="{M + 20}" y="{y + 34:.1f}" font-size="22" font-weight="700" fill="#F5F8FC">{esc(clip(repo["name"], 40))}</text>')
        out.append(f'<text class="s" x="{M + 20}" y="{y + 58:.1f}" font-size="13.5" fill="#B9C6D8">{esc(clip(repo["description"], 96))}</text>')
        out.append(f'<circle cx="{M + 26}" cy="{y + 76:.1f}" r="3.5" fill="{lang_color}"/>')
        out.append(
            f'<text class="m" x="{M + 36}" y="{y + 80:.1f}" font-size="10.5" letter-spacing="1.2" fill="#6D7E94">'
            f'<tspan fill="#B6C3D4">{esc(clip(repo["language"], 14)).upper()}</tspan> · {esc(repo["owner"])} · {ownership} · {esc(repo["kind"].upper())}</text>'
        )
        out.append(f'<text class="m" x="1224" y="{y + 34:.1f}" text-anchor="end" font-size="11" letter-spacing="1.4" fill="{accent}">OPEN REPOSITORY ↗</text>')
        out.append(f'<text class="m" x="1224" y="{y + 58:.1f}" text-anchor="end" font-size="11.5" fill="#8FA1B6">★ {repo["stars"]:02d} · FORKS {repo["forks"]:02d}</text>')
        out.append(f'<text class="m" x="1224" y="{y + 80:.1f}" text-anchor="end" font-size="10.5" letter-spacing="1" fill="#6D7E94">UPDATED {esc(updated)}</text>')
        out.append("</g>")

    status = "CACHED SNAPSHOT" if cached else "SYNC OK"
    status_color = "#C08A1E" if cached else "#6C9FE0"
    footer_y = ROW_TOP + ROWS * ROW_H + 6
    out.append(f'<rect x="{M}" y="{footer_y:.1f}" width="{CONTENT_W}" height="1" fill="#1E2C48" fill-opacity=".7"/>')
    out.append(f'<circle class="pulse" cx="62" cy="{footer_y + 30:.1f}" r="3" fill="{status_color}"/>')
    out.append(f'<text class="m" x="76" y="{footer_y + 34:.1f}" font-size="11" fill="{status_color}">{status}</text>')
    out.append(f'<text class="m" x="{M + 120}" y="{footer_y + 34:.1f}" font-size="11" fill="#8FA1B6">live metadata · refreshed every three hours</text>')
    out.append(f'<text class="m" x="1224" y="{footer_y + 34:.1f}" text-anchor="end" font-size="11" fill="#6D7E94">github.com/{esc(USER)}?tab=repositories</text>')

    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#1E2C48" stroke-opacity=".4"/>')
    out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    target = REPO_ROOT / "assets" / "repos.svg"
    target.write_text(render(), encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
