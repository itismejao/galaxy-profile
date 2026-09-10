"""SVG template: neofetch-style terminal card (850x430).

Renders a fake terminal window that prints profile "system info" the way
`neofetch` does — an ASCII planet on the left, key/value stats on the right,
and a theme color palette at the bottom. Lines fade in sequentially with a
blinking block cursor to sell the "typing" effect.
"""

from generator.utils import esc

WIDTH, HEIGHT = 850, 430

TITLE_BAR = 42
ART_X = 44
INFO_X = 300
BODY_TOP = 88
INFO_LINE_H = 26
ART_LINE_H = 20

# Compact ASCII planet-with-ring, rendered one <text> per line.
ART = [
    "        .  *   .    ",
    "     *    _____   . ",
    "      ,-'`     `'-.  ",
    "    /`   .---.    `\\ ",
    "   |    ( o o )    | ",
    "  -+-----`. .`-----+-",
    "   |     `---`     | ",
    "    \\             /  ",
    "  .  `-._____.-'  *  ",
    "     *   .    .  .   ",
]


def render(data: dict, theme: dict) -> str:
    """Render the terminal card SVG.

    Args:
        data: prepared dict from SVGBuilder.render_terminal_card with keys:
            handle, prompt, rows (list of {label, value, color}), langs, uptime
        theme: color palette dict
    """
    accent = theme["synapse_cyan"]
    violet = theme["dendrite_violet"]
    amber = theme["axon_amber"]

    handle = esc(data["handle"])
    prompt = esc(data["prompt"])
    rows = data["rows"]
    rule = "─" * min(len(data["handle"]), 30)

    # --- ASCII art (left column) ---
    art_lines = []
    for i, line in enumerate(ART):
        y = BODY_TOP + 26 + i * ART_LINE_H
        delay = f"{0.15 + i * 0.05:.2f}s"
        art_lines.append(
            f'    <text x="{ART_X}" y="{y}" class="reveal" style="animation-delay:{delay}" '
            f'xml:space="preserve" fill="{accent}" font-size="13" '
            f'font-family="monospace" opacity="0.9">{esc(line)}</text>'
        )
    art_str = "\n".join(art_lines)

    # --- Info block (right column) ---
    info_lines = []
    # header: handle + rule
    info_lines.append(
        f'    <text x="{INFO_X}" y="{BODY_TOP + 12}" class="reveal" style="animation-delay:0.1s" '
        f'fill="{amber}" font-size="15" font-weight="bold" font-family="monospace">{handle}</text>'
    )
    info_lines.append(
        f'    <text x="{INFO_X}" y="{BODY_TOP + 30}" class="reveal" style="animation-delay:0.2s" '
        f'xml:space="preserve" fill="{theme["text_faint"]}" font-size="14" font-family="monospace">{esc(rule)}</text>'
    )

    label_w = max((len(r["label"]) for r in rows), default=8) + 1
    for i, row in enumerate(rows):
        y = BODY_TOP + 56 + i * INFO_LINE_H
        delay = f"{0.35 + i * 0.12:.2f}s"
        label = esc(row["label"].ljust(label_w))
        value = esc(row["value"])
        value_color = theme.get(row.get("color", "text_bright"), theme["text_bright"])
        info_lines.append(
            f'    <text x="{INFO_X}" y="{y}" class="reveal" style="animation-delay:{delay}" '
            f'xml:space="preserve" font-size="14" font-family="monospace">'
            f'<tspan fill="{violet}" font-weight="bold">{label}</tspan>'
            f'<tspan fill="{value_color}">{value}</tspan></text>'
        )
    info_str = "\n".join(info_lines)

    # --- Theme color palette (bottom) ---
    swatch_keys = [
        "void", "nebula", "star_dust", "synapse_cyan",
        "dendrite_violet", "axon_amber", "text_dim", "text_bright",
    ]
    sw = 26
    pal_y = HEIGHT - 46
    swatches = []
    for i, key in enumerate(swatch_keys):
        x = INFO_X + i * (sw + 6)
        swatches.append(
            f'    <rect x="{x}" y="{pal_y}" width="{sw}" height="{sw}" rx="4" '
            f'fill="{theme[key]}" stroke="{theme["star_dust"]}" stroke-width="1" '
            f'class="reveal" style="animation-delay:{1.6 + i * 0.06:.2f}s"/>'
        )
    palette_str = "\n".join(swatches)

    # Blinking cursor sits after the prompt line.
    cursor_x = 44 + (len(data["prompt"]) + 1) * 8.4

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .reveal {{ opacity: 0; animation: reveal 0.45s ease forwards; }}
      @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      .cursor {{ animation: blink 1.1s step-end infinite; }}
      @keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
      .dot {{ animation: glow 4s ease-in-out infinite; }}
      @keyframes glow {{ 0%, 100% {{ opacity: 0.85; }} 50% {{ opacity: 1; }} }}
    </style>
    <filter id="term-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="0.6"/>
    </filter>
  </defs>

  <!-- Window -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['void']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Title bar -->
  <path d="M0.5 12.5 A12 12 0 0 1 12.5 0.5 H{WIDTH - 12.5} A12 12 0 0 1 {WIDTH - 0.5} 12.5 V{TITLE_BAR} H0.5 Z"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>
  <circle class="dot" cx="24" cy="21" r="6" fill="#ff5f56"/>
  <circle class="dot" cx="44" cy="21" r="6" fill="#ffbd2e"/>
  <circle class="dot" cx="64" cy="21" r="6" fill="#27c93f"/>
  <text x="{WIDTH / 2}" y="26" text-anchor="middle" fill="{theme['text_dim']}"
        font-size="13" font-family="monospace">{handle} — -bash</text>

  <!-- Prompt line -->
  <text x="44" y="{BODY_TOP - 18}" fill="{theme['text_bright']}" font-size="14" font-family="monospace" filter="url(#term-glow)"><tspan fill="{theme['synapse_cyan']}" font-weight="bold">➜</tspan> <tspan fill="{theme['dendrite_violet']}">~</tspan> {prompt}</text>
  <rect class="cursor" x="{cursor_x:.1f}" y="{BODY_TOP - 30}" width="9" height="16" fill="{theme['synapse_cyan']}"/>

{art_str}

{info_str}

  <!-- Theme palette -->
  <text x="{INFO_X}" y="{pal_y - 8}" fill="{theme['text_faint']}" font-size="10" font-family="monospace" letter-spacing="2">THEME</text>
{palette_str}
</svg>'''
