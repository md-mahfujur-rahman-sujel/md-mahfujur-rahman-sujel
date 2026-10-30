#!/usr/bin/env python3
"""Render the live repository index (assets/repos.svg)."""

from __future__ import annotations

from common import (
    LANG_COLORS,
    REPO_ROOT,
    USER,
    clip,
    esc,
    fetch_repo,
    now_utc,
    relative_day,
    stamp,
)

W, H = 1280, 432
PAD = 20.0
ROW_X = PAD
ROW_W = W - PAD * 2
ROW_H = 86.0
ROW_GAP = 10.0
ROWS_Y = 100.0

REPOS = [
    {
        "full": "md-mahfujur-rahman-sujel/Apex-Arcade",
        "name": "Apex Arcade",
        "node": "01",
        "accent": "#FFB4B4",
        "kind": "web",
        "fallback_desc": "React launcher for 50 browser games with history, favorites and score cards.",
        "fallback_lang": "HTML",
        "fallback_stack": "React · TypeScript · Vite",
    },
    {
        "full": "md-mahfujur-rahman-sujel/Unrot",
        "name": "Unrot",
        "node": "02",
        "accent": "#6C9FE0",
        "kind": "android",
        "fallback_desc": "Locks distracting apps behind a focus timer; earn time back with math challenges.",
        "fallback_lang": "Kotlin",
        "fallback_stack": "Android · Kotlin · Product Design",
    },
    {
        "full": "masum-mir/Oppzy",
        "name": "Oppzy",
        "node": "03",
        "accent": "#FF6B6B",
        "kind": "web",
        "fallback_desc": "Internship and research matching platform, built as a team project with Spring Boot.",
        "fallback_lang": "JavaScript",
        "fallback_stack": "Spring Boot · React · MySQL",
    },
]

CSS = """
.s{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
.m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.pulse{animation:pulse 2.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.rise{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
.sweep{animation:sweep 8s linear infinite}
@keyframes sweep{from{transform:translateX(-420px)}to{transform:translateX(1320px)}}
@media (prefers-reduced-motion:reduce){.pulse,.rise,.sweep{animation:none!important}}
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
    out.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#060A13"/><stop offset=".55" stop-color="#0A1120"/><stop offset="1" stop-color="#060A13"/></linearGradient>')
    out.append('<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1E2C48" stop-opacity=".24"/><stop offset=".55" stop-color="#14213A" stop-opacity=".5"/><stop offset="1" stop-color="#6C9FE0" stop-opacity=".05"/></linearGradient>')
    out.append('<linearGradient id="scanline" x1="0" x2="1"><stop offset="0" stop-color="#6C9FE0" stop-opacity="0"/><stop offset=".5" stop-color="#6C9FE0" stop-opacity=".09"/><stop offset="1" stop-color="#6C9FE0" stop-opacity="0"/></linearGradient>')
    out.append('<radialGradient id="bloomBlue"><stop offset="0" stop-color="#D9232E" stop-opacity=".2"/><stop offset="1" stop-color="#D9232E" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="bloomMid"><stop offset="0" stop-color="#FF6B6B" stop-opacity=".14"/><stop offset="1" stop-color="#FF6B6B" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="bloomCyan"><stop offset="0" stop-color="#6C9FE0" stop-opacity=".12"/><stop offset="1" stop-color="#6C9FE0" stop-opacity="0"/></radialGradient>')
    out.append('<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#1E2C48" stroke-opacity=".14"/></pattern>')
    out.append('<pattern id="scan" width="6" height="4" patternUnits="userSpaceOnUse"><rect width="6" height="1" fill="#000000" opacity=".14"/></pattern>')
    out.append(f'<clipPath id="win"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    out.append(f'<clipPath id="body"><rect x="0" y="88" width="{W}" height="{H - 134}"/></clipPath>')
    out.append(f"<style>{CSS}</style>")
    out.append("</defs>")

    out.append('<g clip-path="url(#win)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    out.append('<ellipse cx="180" cy="120" rx="380" ry="260" fill="url(#bloomBlue)"/>')
    out.append('<ellipse cx="760" cy="260" rx="420" ry="250" fill="url(#bloomMid)"/>')
    out.append('<ellipse cx="1160" cy="120" rx="320" ry="240" fill="url(#bloomCyan)"/>')
    out.append('<g fill="none" stroke="#F5F8FC" stroke-width="1" stroke-opacity=".05"><path d="M1280 0L1231 598M1280 0L1079 553M1280 0L943 477M1280 0L833 367M1280 0L757 231M1280 0L722 79"/><path d="M1280 180A180 180 0 0 1 1100 0M1280 320A320 320 0 0 1 960 0M1280 460A460 460 0 0 1 820 0M1280 600A600 600 0 0 1 680 0"/></g>')

    # window chrome
    out.append('<rect width="1280" height="46" fill="#0A1121" fill-opacity=".94"/><rect y="45" width="1280" height="1" fill="#1E2C48"/>')
    out.append('<circle cx="22" cy="23" r="5.5" fill="#D9232E" fill-opacity=".8" stroke="#D9232E"/><circle cx="40" cy="23" r="5.5" fill="#FFB4B4" fill-opacity=".8" stroke="#FFB4B4"/><circle cx="58" cy="23" r="5.5" fill="#6C9FE0" fill-opacity=".7" stroke="#6C9FE0"/>')
    out.append('<text class="m" x="640" y="28" text-anchor="middle" font-size="12" fill="#9BACC0">sujel@ewu: ~/repos --index</text>')
    out.append('<rect x="1000" y="11" width="86" height="24" rx="12" fill="#D9232E" fill-opacity=".16" stroke="#D9232E" stroke-opacity=".8"/>')
    out.append('<circle class="pulse" cx="1018" cy="23" r="3" fill="#D9232E"/><text class="m" x="1027" y="27" font-size="9" letter-spacing="1.4" fill="#F5F8FC">LIVE</text>')
    out.append(f'<text class="m" x="1258" y="27" text-anchor="end" font-size="10.5" fill="#8FA1B6">{esc(stamp(now))}</text>')

    # header strip
    out.append('<rect y="46" width="1280" height="42" fill="#080E1A" fill-opacity=".9"/><rect y="87" width="1280" height="1" fill="#1E2C48"/>')
    out.append('<circle cx="30" cy="67" r="4" fill="#FFB4B4"/><circle cx="30" cy="67" r="8" fill="#FFB4B4" fill-opacity=".12"/>')
    out.append('<text class="m" x="46" y="71" font-size="11.5" letter-spacing="2" fill="#B6C3D4">REPOSITORY INDEX</text>')
    out.append(f'<text class="m" x="228" y="71" font-size="10" letter-spacing="1" fill="#8FA1B6">~/repos/index.json</text>')

    chips = [
        (f"ALL {len(repos):02d}", "#FFB4B4", True),
        (f"OWNED {owned:02d}", "#6C9FE0", False),
        (f"COLLAB {collab:02d}", "#FF6B6B", False),
        (f"LANGS {len(languages):02d}", "#D9232E", False),
    ]
    chip_x = 500.0
    for label, color, active in chips:
        chip_w = 34 + len(label) * 6.6
        fill = color if active else "#0B1424"
        out.append(
            f'<rect x="{chip_x:.1f}" y="57" width="{chip_w:.1f}" height="21" rx="5" '
            f'fill="{fill}" fill-opacity="{".16" if active else ".7"}" stroke="{color}" stroke-opacity="{".8" if active else ".35"}"/>'
        )
        out.append(
            f'<text class="m" x="{chip_x + chip_w / 2:.1f}" y="71.5" text-anchor="middle" font-size="9" '
            f'letter-spacing="1.1" fill="{color if active else "#8FA1B6"}">{label}</text>'
        )
        chip_x += chip_w + 8
    out.append(f'<text class="m" x="1196" y="71" text-anchor="end" font-size="10" letter-spacing="1" fill="#8FA1B6">ORDER · NODE ID</text>')
    out.append('<circle class="pulse" cx="1210" cy="67" r="2.6" fill="#6C9FE0"/>')
    out.append('<text class="m" x="1260" y="71" text-anchor="end" font-size="10" letter-spacing="1" fill="#6C9FE0">SYNC</text>')

    # repo rows
    out.append('<g clip-path="url(#body)">')
    for index, repo in enumerate(repos):
        y = ROWS_Y + index * (ROW_H + ROW_GAP)
        accent = repo["accent"]
        cta = "#FFDADA" if accent == "#D9232E" else accent
        lang_color = LANG_COLORS.get(repo["language"], accent)
        updated = "PENDING" if repo["updated"] == "—" else repo["updated"].upper()
        out.append(
            f'<g class="rise" style="animation-delay:{0.08 * index:.2f}s">'
            f'<rect x="{ROW_X}" y="{y}" width="{ROW_W}" height="{ROW_H}" rx="12" fill="url(#glass)" stroke="#1E2C48" stroke-opacity=".6"/>'
            f'<rect x="{ROW_X}" y="{y + 12}" width="3" height="{ROW_H - 24}" rx="1.5" fill="{accent}"/>'
            f'<rect x="{ROW_X}" y="{y}" width="{ROW_W}" height="1.5" rx=".75" fill="{accent}" fill-opacity=".55"/>'
            f'<text class="m" x="{ROW_X + 22}" y="{y + 35}" font-size="11.5" fill="{accent}">{repo["node"]}</text>'
            f'<text class="m" x="{ROW_X + 22}" y="{y + 52}" font-size="9" letter-spacing="1.1" fill="#6D7E94">NODE</text>'
            f'<text class="s" x="{ROW_X + 68}" y="{y + 34}" font-size="20" font-weight="700" fill="#F5F8FC">{esc(clip(repo["name"], 48))}</text>'
            f'<text class="m" x="{ROW_X + 68}" y="{y + 52}" font-size="10.5" fill="#8FA1B6">{esc(repo["owner"])}{"" if repo["owner"] == USER else " · COLLABORATOR"}</text>'
            f'<text class="s" x="{ROW_X + 68}" y="{y + 72}" font-size="14" fill="#CAD5E1">{esc(clip(repo["description"], 108))}</text>'
        )
        out.append(f'<text class="m" x="{ROW_X + 22}" y="{y + 72}" font-size="9" letter-spacing=".8" fill="{accent}" fill-opacity=".55">{esc(repo["kind"].upper())}</text>')
        out.append(
            f'<text class="m" x="{ROW_X + ROW_W - 20}" y="{y + 34}" text-anchor="end" font-size="10.5" letter-spacing="1.3" fill="{cta}">OPEN REPOSITORY ↗</text>'
            f'<text class="m" x="{ROW_X + ROW_W - 20}" y="{y + 52}" text-anchor="end" font-size="10.5" letter-spacing=".8" fill="#8FA1B6">UPDATED {esc(updated)}</text>'
            f'<circle cx="{ROW_X + ROW_W - 268}" cy="{y + 66}" r="4" fill="{lang_color}"/>'
            f'<text class="m" x="{ROW_X + ROW_W - 258}" y="{y + 70}" font-size="12" fill="#B6C3D4">{esc(clip(repo["language"], 10))}</text>'
            f'<text class="m" x="{ROW_X + ROW_W - 172}" y="{y + 70}" font-size="12" fill="#8FA1B6">★ {repo["stars"]:02d}</text>'
            f'<text class="m" x="{ROW_X + ROW_W - 108}" y="{y + 70}" font-size="12" fill="#8FA1B6">⑂ {repo["forks"]:02d}</text>'
        )
        out.append('</g>')

    out.append('<rect class="sweep" x="0" y="88" width="420" height="260" fill="url(#scanline)"/>')
    out.append("</g>")

    # footer
    footer_y = H - 46
    out.append(f'<rect y="{footer_y}" width="1280" height="46" fill="#080E1A" fill-opacity=".94"/><rect y="{footer_y}" width="1280" height="1" fill="#1E2C48"/>')
    out.append(f'<text class="m" x="20" y="{footer_y + 28}" font-size="11" fill="#8FA1B6">{len(repos)} repositories · {owned} owned · {collab} collaborator · {"cached snapshot" if cached else "live github api"}</text>')
    status = "CACHED SNAPSHOT" if cached else "SYNC OK"
    status_color = "#C08A1E" if cached else "#6C9FE0"
    out.append(f'<circle class="pulse" cx="620" cy="{footer_y + 24}" r="3" fill="{status_color}"/>')
    out.append(f'<text class="m" x="630" y="{footer_y + 28}" font-size="10.5" fill="{status_color}">{status}</text>')
    out.append(f'<text class="m" x="1260" y="{footer_y + 28}" text-anchor="end" font-size="11" fill="#8FA1B6">github.com/{esc(USER)}?tab=repositories</text>')

    out.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    out.append("</g>")
    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="#1E2C48" stroke-opacity=".45"/>')
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    target = REPO_ROOT / "assets" / "repos.svg"
    target.write_text(render(), encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
