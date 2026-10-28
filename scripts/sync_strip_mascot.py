#!/usr/bin/env python3
"""Copy assets/mascot.svg into the mascot slot of assets/flight-v4.svg."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OPEN_ANCHOR = '<g class="fly"'
CLOSE_ANCHOR = "</g></g></g></g></g></g>"


def mascot_inner() -> str:
    svg = (ASSETS / "mascot.svg").read_text(encoding="utf-8").strip()
    if not svg.startswith("<svg") or not svg.endswith("</svg>"):
        raise SystemExit("mascot.svg: expected a bare <svg> root")
    return svg[svg.index(">") + 1 : -len("</svg>")].strip()


def main() -> None:
    strip_path = ASSETS / "flight-v4.svg"
    lines = strip_path.read_text(encoding="utf-8").splitlines()
    starts = [i for i, ln in enumerate(lines) if OPEN_ANCHOR in ln]
    ends = [i for i, ln in enumerate(lines) if ln.strip() == CLOSE_ANCHOR]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise SystemExit("flight-v4.svg: could not locate exactly one mascot slot")
    body = mascot_inner().splitlines()
    out = lines[: starts[0] + 1] + body + lines[ends[0] :]
    text = "\n".join(out) + "\n"
    strip_path.write_text(text, encoding="utf-8")
    print(f"{strip_path} {len(text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
