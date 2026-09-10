"""SVG template: unified profile card.

Stacks the galaxy (top), the neofetch terminal (middle) and the social chips
(bottom) into a single SVG over one continuous starfield, so the three read as
one cohesive piece. Sub-SVGs are embedded as nested <svg> viewports with their
own backgrounds turned off; this card supplies the shared void + stars.
"""

from generator.utils import deterministic_random

WIDTH = 1000
PAD = 22
GAP = 16
CHIP_W, CHIP_H = 330, 92
SIDE = 40          # horizontal margin for the chip row


def _starfield(seed, width, height, theme):
    layers = [
        {"count": 90, "lbl": "bg", "r": (0.3, 0.9), "o": (0.06, 0.28)},
        {"count": 40, "lbl": "mid", "r": (0.6, 1.2), "o": (0.12, 0.45)},
        {"count": 18, "lbl": "fg", "r": (1.0, 1.7), "o": (0.35, 0.65)},
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


def _embed(inner_svg, x, y, dw, dh, viewbox, overflow="visible"):
    """Place a sub-SVG as a nested viewport at (x, y) scaled to dw x dh."""
    return (
        f'  <svg x="{x:.1f}" y="{y:.1f}" width="{dw:.1f}" height="{dh:.1f}" '
        f'viewBox="{viewbox}" overflow="{overflow}">\n{inner_svg}\n  </svg>'
    )


# Galaxy has empty margins top (no name/tagline) and a little at the bottom;
# crop them via the embedded viewBox so it sits tight in the stack.
G_CROP_TOP = 44
G_CROP_BOT = 6
PER_ROW = 3          # chips per row (5 -> 3 + 2)
ROW_GAP = 16


def render(galaxy, terminal, chips, theme, seed="unified"):
    """Compose the unified card.

    Args:
        galaxy: (svg_str, native_w, native_h)
        terminal: (svg_str, native_w, native_h)
        chips: list of chip svg_str (each CHIP_W x CHIP_H native)
        theme: color palette dict
    """
    gsvg, gw, gh = galaxy
    tsvg, tw, th = terminal

    # Galaxy: nearly full width, centered, with its empty top/bottom cropped.
    g_vb_h = gh - G_CROP_TOP - G_CROP_BOT
    g_dw = WIDTH - 2 * PAD - 40
    g_scale = g_dw / gw
    g_dh = g_vb_h * g_scale
    g_x = (WIDTH - g_dw) / 2
    g_y = 8
    g_vb = f"0 {G_CROP_TOP} {gw} {g_vb_h}"

    # Terminal: full content width, tight under the galaxy.
    t_dw = WIDTH - 2 * PAD
    t_scale = t_dw / tw
    t_dh = th * t_scale
    t_x = PAD
    t_y = g_y + g_dh + 2

    # Chips: two centered rows (3 + 2), larger cards.
    per_row = min(PER_ROW, max(len(chips), 1))
    c_dw = (WIDTH - 2 * SIDE - (per_row - 1) * ROW_GAP) / per_row
    c_scale = c_dw / CHIP_W
    c_dh = CHIP_H * c_scale
    rows = [chips[i:i + per_row] for i in range(0, len(chips), per_row)]
    chips_top = t_y + t_dh + GAP + 4

    embeds = [
        _embed(gsvg, g_x, g_y, g_dw, g_dh, g_vb, overflow="hidden"),
        _embed(tsvg, t_x, t_y, t_dw, t_dh, f"0 0 {tw} {th}"),
    ]
    row_y = chips_top
    for row in rows:
        k = len(row)
        total_w = k * c_dw + (k - 1) * ROW_GAP
        start_x = (WIDTH - total_w) / 2
        for j, csvg in enumerate(row):
            cx = start_x + j * (c_dw + ROW_GAP)
            embeds.append(_embed(csvg, cx, row_y, c_dw, c_dh, f"0 0 {CHIP_W} {CHIP_H}"))
        row_y += c_dh + ROW_GAP

    height = int(row_y - ROW_GAP + PAD)
    stars = _starfield(seed, WIDTH, height, theme)
    embeds_str = "\n".join(embeds)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <style>
      .star-bg {{ animation: twinkle-slow 7s ease-in-out infinite; }}
      .star-mid {{ animation: twinkle-mid 5s ease-in-out infinite; }}
      .star-fg {{ animation: twinkle-fast 3s ease-in-out infinite; }}
      @keyframes twinkle-slow {{ 0%, 100% {{ opacity: 0.08; }} 50% {{ opacity: 0.3; }} }}
      @keyframes twinkle-mid {{ 0%, 100% {{ opacity: 0.15; }} 50% {{ opacity: 0.5; }} }}
      @keyframes twinkle-fast {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 0.8; }} }}
    </style>
    <clipPath id="unified-clip">
      <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="16" ry="16"/>
    </clipPath>
  </defs>

  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="16" ry="16"
        fill="{theme['void']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <g clip-path="url(#unified-clip)">
{stars}
  </g>

{embeds_str}
</svg>'''
