"""SVG template: a single social "comms channel" chip (330x92).

One clickable, space-console-styled button per social link — icon in a glowing
node, platform label, handle, and a witty subtitle. Meant to sit in a row below
the galaxy; each chip is wrapped in an <a href> in the README.
"""

from generator.utils import esc, deterministic_random

WIDTH, HEIGHT = 330, 92


def _stars(seed, theme):
    sx = deterministic_random(f"{seed}_x", 16, 6, WIDTH - 6)
    sy = deterministic_random(f"{seed}_y", 16, 6, HEIGHT - 6)
    sr = deterministic_random(f"{seed}_r", 16, 0.3, 1.1)
    so = deterministic_random(f"{seed}_o", 16, 0.1, 0.45)
    sd = deterministic_random(f"{seed}_d", 16, 0.0, 4.0)
    out = []
    for i in range(16):
        out.append(
            f'    <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.2f}" fill="#ffffff" '
            f'opacity="{so[i]:.2f}" class="tw" style="animation-delay:{sd[i] * 0.3:.1f}s"/>'
        )
    return "\n".join(out)


def render(chip: dict, theme: dict) -> str:
    """Render one social chip.

    Args:
        chip: dict with keys label, handle, quip, icon, color (theme key), seed
        theme: color palette dict
    """
    c = chip.get("color", "synapse_cyan")
    color = c if isinstance(c, str) and c.startswith("#") else theme.get(c, theme["synapse_cyan"])
    icon = chip["icon"]
    stars = _stars(chip.get("seed", chip["label"]), theme)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .tw {{ animation: tw 4s ease-in-out infinite; }}
      @keyframes tw {{ 0%, 100% {{ opacity: 0.15; }} 50% {{ opacity: 0.5; }} }}
      .beacon {{ animation: beacon 2.2s ease-in-out infinite; }}
      @keyframes beacon {{ 0%, 100% {{ opacity: 0.35; }} 50% {{ opacity: 1; }} }}
      .chip:hover .plate {{ stroke-opacity: 0.9; }}
    </style>
    <clipPath id="clip-{chip['key']}">
      <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="14" ry="14"/>
    </clipPath>
    <radialGradient id="node-{chip['key']}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <g class="chip">
    <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="14" ry="14"
          fill="{theme['void']}" stroke="{theme['star_dust']}" stroke-width="1"/>
    <g clip-path="url(#clip-{chip['key']})">
{stars}
      <rect class="plate" x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="14" ry="14"
            fill="none" stroke="{color}" stroke-width="1" stroke-opacity="0.4"/>
      <rect x="1" y="1" width="5" height="{HEIGHT - 2}" fill="{color}" opacity="0.55"/>
    </g>

    <!-- signal node -->
    <circle cx="48" cy="46" r="26" fill="url(#node-{chip['key']})"/>
    <circle cx="48" cy="46" r="20" fill="{theme['nebula']}" stroke="{color}" stroke-width="1.2" opacity="0.9"/>
    <svg x="36" y="34" width="24" height="24" viewBox="0 0 24 24" fill="{color}">{icon}</svg>

    <!-- beacon -->
    <circle class="beacon" cx="{WIDTH - 18}" cy="18" r="3" fill="{color}"/>

    <!-- text -->
    <text x="86" y="38" fill="{color}" font-size="16" font-weight="bold" font-family="monospace">{esc(chip['label'])}</text>
    <text x="86" y="57" fill="{theme['text_bright']}" font-size="12" font-family="monospace">{esc(chip['handle'])}</text>
    <text x="86" y="74" fill="{theme['text_faint']}" font-size="10" font-family="monospace" font-style="italic">{esc(chip['quip'])}</text>
  </g>
</svg>'''
