"""SVG template: neofetch-style profile card.

Renders an ASCII portrait on the left and dotted-leader "system info" lines
on the right (amber labels, right-aligned values, section headers, and a
green/red Lines-of-Code split), the way `neofetch` prints on a login shell.
Lines fade in sequentially with a blinking cursor to sell the "printing" feel.
"""

from generator.utils import esc, deterministic_random

WIDTH = 1000
PAD_TOP = 40
LINE_H = 22
INFO_X = 470
INFO_RIGHT = WIDTH - 36
CHARW = 8.4          # monospace advance at font-size 14

ASCII_X = 40
ASCII_TOP = 40
ASCII_LH = 16.5
ASCII_FS = 15

LOC_ADD = "#3fb950"  # github green
LOC_DEL = "#f85149"  # github red


def _starfield(seed, width, height, theme):
    """Twinkling star layers matching the galaxy header's background."""
    layers = [
        {"count": 60, "lbl": "bg", "r": (0.3, 0.9), "o": (0.06, 0.28)},
        {"count": 28, "lbl": "mid", "r": (0.6, 1.2), "o": (0.12, 0.45)},
        {"count": 12, "lbl": "fg", "r": (1.0, 1.7), "o": (0.35, 0.65)},
    ]
    accent = {
        0: theme.get("synapse_cyan", "#00d4ff"),
        5: theme.get("dendrite_violet", "#a78bfa"),
        9: theme.get("axon_amber", "#ffb020"),
    }
    out = []
    for L in layers:
        n, lbl = L["count"], L["lbl"]
        sx = deterministic_random(f"{seed}_x_{lbl}", n, 8, width - 8)
        sy = deterministic_random(f"{seed}_y_{lbl}", n, 8, height - 8)
        sr = deterministic_random(f"{seed}_r_{lbl}", n, L["r"][0], L["r"][1])
        so = deterministic_random(f"{seed}_o_{lbl}", n, L["o"][0], L["o"][1])
        sd = deterministic_random(f"{seed}_d_{lbl}", n, 0.0, 4.0)
        for i in range(n):
            fill = accent.get(i % 13, "#ffffff")
            out.append(
                f'    <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.2f}" '
                f'fill="{fill}" opacity="{so[i]:.2f}" class="star-{lbl}" '
                f'style="animation-delay:{sd[i] * 0.3:.1f}s"/>'
            )
    return "\n".join(out)


def _leader(y, label, value, value_color, theme, delay):
    """A 'label ....... value' line with a right-aligned value."""
    prefix = f"· {label}:"          # "· label:"
    left_x = INFO_X
    val_x = INFO_RIGHT
    dot_start = left_x + len(prefix) * CHARW + CHARW
    dot_end = val_x - len(value) * CHARW - CHARW
    ndots = int((dot_end - dot_start) / CHARW)
    dots_svg = ""
    if ndots > 0:
        dots_svg = (
            f'      <text x="{dot_start:.1f}" y="{y}" fill="{theme["star_dust"]}" '
            f'font-size="14" font-family="monospace" letter-spacing="1">{"." * ndots}</text>\n'
        )
    return (
        f'    <g class="reveal" style="animation-delay:{delay}">\n'
        f'      <text x="{left_x}" y="{y}" xml:space="preserve" font-size="14" font-family="monospace">'
        f'<tspan fill="{theme["axon_amber"]}">&#183; </tspan>'
        f'<tspan fill="{theme["axon_amber"]}" font-weight="bold">{esc(label)}:</tspan></text>\n'
        f'{dots_svg}'
        f'      <text x="{val_x}" y="{y}" text-anchor="end" fill="{value_color}" font-size="14" font-family="monospace">{esc(value)}</text>\n'
        f'    </g>'
    )


def _leader_loc(y, label, total, added, removed, theme, delay):
    """The Lines-of-Code line: right-aligned 'total (added++, removed--)'."""
    prefix = f"· {label}:"
    plain = f"{total} ({added}++, {removed}--)"
    left_x = INFO_X
    val_start = INFO_RIGHT - len(plain) * CHARW
    dot_start = left_x + len(prefix) * CHARW + CHARW
    ndots = int((val_start - dot_start - CHARW) / CHARW)
    dots_svg = ""
    if ndots > 0:
        dots_svg = (
            f'      <text x="{dot_start:.1f}" y="{y}" fill="{theme["star_dust"]}" '
            f'font-size="14" font-family="monospace" letter-spacing="1">{"." * ndots}</text>\n'
        )
    return (
        f'    <g class="reveal" style="animation-delay:{delay}">\n'
        f'      <text x="{left_x}" y="{y}" xml:space="preserve" font-size="14" font-family="monospace">'
        f'<tspan fill="{theme["axon_amber"]}">&#183; </tspan>'
        f'<tspan fill="{theme["axon_amber"]}" font-weight="bold">{esc(label)}:</tspan></text>\n'
        f'{dots_svg}'
        f'      <text x="{val_start:.1f}" y="{y}" xml:space="preserve" font-size="14" font-family="monospace">'
        f'<tspan fill="{theme["synapse_cyan"]}">{esc(total)}</tspan>'
        f'<tspan fill="{theme["text_dim"]}"> (</tspan>'
        f'<tspan fill="{LOC_ADD}">{esc(added)}++</tspan>'
        f'<tspan fill="{theme["text_dim"]}">, </tspan>'
        f'<tspan fill="{LOC_DEL}">{esc(removed)}--</tspan>'
        f'<tspan fill="{theme["text_dim"]}">)</tspan></text>\n'
        f'    </g>'
    )


def render(data: dict, theme: dict) -> str:
    """Render the neofetch-style card.

    Args:
        data: dict with keys:
            handle: "user@github"
            art:    list[str] ASCII portrait lines
            lines:  list of row dicts (see SVGBuilder._terminal_data):
                {"type": "header"|"section"|"blank"|"leader"|"loc", ...}
        theme: color palette dict
    """
    art = data["art"]
    lines = data["lines"]
    handle = data["handle"]

    height = max(
        PAD_TOP + len(lines) * LINE_H + 20,
        ASCII_TOP + len(art) * ASCII_LH + 24,
    )
    height = int(height)

    stars_str = _starfield(data["handle"], WIDTH, height, theme)

    # --- ASCII portrait (vertically centered in the panel) ---
    art_top = max(ASCII_TOP, (height - len(art) * ASCII_LH) / 2)
    art_rows = []
    for i, line in enumerate(art):
        y = art_top + (i + 1) * ASCII_LH
        art_rows.append(
            f'    <text x="{ASCII_X}" y="{y:.1f}" xml:space="preserve" '
            f'class="reveal" style="animation-delay:{0.05 + i * 0.03:.2f}s" '
            f'fill="{theme["text_dim"]}" font-size="{ASCII_FS}" font-family="monospace">{esc(line)}</text>'
        )
    art_str = "\n".join(art_rows)

    # --- Info lines ---
    info_rows = []
    last_y = PAD_TOP
    delay = 0.2
    for row in lines:
        delay += 0.09
        d = f"{delay:.2f}s"
        rtype = row["type"]
        if rtype == "blank":
            last_y += LINE_H // 2 + 4
            continue
        last_y += LINE_H
        y = last_y
        if rtype == "header":
            text_len = len(row["text"])
            rule_x = INFO_X + (text_len + 1) * CHARW
            info_rows.append(
                f'    <g class="reveal" style="animation-delay:{d}">\n'
                f'      <text x="{INFO_X}" y="{y}" fill="{theme["synapse_cyan"]}" font-size="15" '
                f'font-weight="bold" font-family="monospace">{esc(row["text"])}</text>\n'
                f'      <line x1="{rule_x:.1f}" y1="{y - 5}" x2="{INFO_RIGHT}" y2="{y - 5}" '
                f'stroke="{theme["star_dust"]}" stroke-width="1"/>\n'
                f'    </g>'
            )
        elif rtype == "section":
            info_rows.append(
                f'    <text x="{INFO_X}" y="{y}" class="reveal" style="animation-delay:{d}" '
                f'fill="{theme["text_faint"]}" font-size="13" font-family="monospace" '
                f'letter-spacing="1">&#9472; {esc(row["text"])}</text>'
            )
        elif rtype == "loc":
            info_rows.append(
                _leader_loc(y, row["label"], row["total"], row["added"], row["removed"], theme, d)
            )
        else:  # leader
            color = theme.get(row.get("color", "synapse_cyan"), theme["synapse_cyan"])
            info_rows.append(_leader(y, row["label"], row["value"], color, theme, d))
    info_str = "\n".join(info_rows)

    cursor_y = last_y + 6
    cursor_delay = f"{delay + 0.2:.2f}s"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <style>
      .reveal {{ opacity: 0; animation: reveal 0.4s ease forwards; }}
      @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      .cursor {{ opacity: 0; animation: appear 0.1s linear {cursor_delay} forwards, blink 1.1s step-end {cursor_delay} infinite; }}
      @keyframes appear {{ to {{ opacity: 1; }} }}
      @keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
      .star-bg {{ animation: twinkle-slow 7s ease-in-out infinite; }}
      .star-mid {{ animation: twinkle-mid 5s ease-in-out infinite; }}
      .star-fg {{ animation: twinkle-fast 3s ease-in-out infinite; }}
      @keyframes twinkle-slow {{ 0%, 100% {{ opacity: 0.08; }} 50% {{ opacity: 0.3; }} }}
      @keyframes twinkle-mid {{ 0%, 100% {{ opacity: 0.15; }} 50% {{ opacity: 0.5; }} }}
      @keyframes twinkle-fast {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 0.8; }} }}
    </style>
    <clipPath id="panel-clip">
      <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" ry="10"/>
    </clipPath>
  </defs>

  <!-- Panel -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" ry="10"
        fill="{theme['void']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Starfield (matches the galaxy header) -->
  <g clip-path="url(#panel-clip)">
{stars_str}
  </g>

{art_str}

{info_str}

  <rect class="cursor" x="{INFO_X}" y="{cursor_y}" width="9" height="16" fill="{theme['synapse_cyan']}"/>
</svg>'''
