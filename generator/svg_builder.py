"""SVG Builder — orchestrator connecting config, stats, and templates."""

from datetime import date, datetime

from generator.templates import (
    galaxy_header,
    stats_card,
    tech_stack,
    projects_constellation,
    terminal_card,
)
from generator.utils import format_number


class SVGBuilder:
    """Builds all SVG assets from config and GitHub data.

    Expects a config dict that has already been through validate_config(),
    which resolves theme defaults and applies missing optional fields.
    """

    def __init__(self, config: dict, stats: dict, languages: dict):
        self.config = config
        self.stats = stats
        self.languages = languages
        self.theme = config["theme"]
        self.galaxy_arms = config.get("galaxy_arms", [])
        self.projects = config.get("projects", [])

    def render_galaxy_header(self) -> str:
        return galaxy_header.render(
            config=self.config,
            theme=self.theme,
            galaxy_arms=self.galaxy_arms,
            projects=self.projects,
        )

    def render_stats_card(self) -> str:
        metrics = self.config["stats"]["metrics"]
        return stats_card.render(
            stats=self.stats,
            metrics=metrics,
            theme=self.theme,
        )

    def render_tech_stack(self) -> str:
        lang_config = self.config.get("languages", {})
        return tech_stack.render(
            languages=self.languages,
            galaxy_arms=self.galaxy_arms,
            theme=self.theme,
            exclude=lang_config.get("exclude", []),
            max_display=lang_config.get("max_display", 8),
        )

    def render_projects_constellation(self) -> str:
        return projects_constellation.render(
            projects=self.projects,
            galaxy_arms=self.galaxy_arms,
            theme=self.theme,
        )

    def render_terminal_card(self) -> str:
        return terminal_card.render(
            data=self._terminal_data(),
            theme=self.theme,
        )

    def _terminal_data(self) -> dict:
        """Assemble neofetch-style, sectioned rows from config + fetched data."""
        profile = self.config.get("profile", {})
        social = self.config.get("social", {})
        term = self.config.get("terminal", {})
        username = self.config["username"]
        s = self.stats

        lines = [{"type": "header", "text": f"{username}@github"}]

        # --- system ---
        lines.append({"type": "leader", "label": "OS", "value": term.get("os", "GalaxyOS rolling")})
        lines.append({"type": "leader", "label": "Uptime", "value": self._uptime(term.get("born"))})
        host = term.get("host") or profile.get("company") or profile.get("location", "Earth")
        lines.append({"type": "leader", "label": "Host", "value": host})
        kernel = term.get("kernel") or profile.get("tagline", "Software Engineer")
        lines.append({"type": "leader", "label": "Kernel", "value": kernel})
        if term.get("ide"):
            lines.append({"type": "leader", "label": "IDE", "value": term["ide"]})

        # --- languages ---
        lines.append({"type": "blank"})
        lines.append({"type": "leader", "label": "Languages.Programming", "value": self._top_langs()})
        if term.get("languages_human"):
            lines.append({"type": "leader", "label": "Languages.Human", "value": term["languages_human"]})

        # --- contact ---
        contact = []
        if social.get("email"):
            contact.append({"type": "leader", "label": "Email", "value": social["email"], "color": "dendrite_violet"})
        if social.get("linkedin"):
            contact.append({"type": "leader", "label": "LinkedIn", "value": social["linkedin"], "color": "dendrite_violet"})
        contact.append({"type": "leader", "label": "GitHub", "value": username, "color": "dendrite_violet"})
        for key, label in (("instagram", "Instagram"), ("discord", "Discord")):
            if term.get(key):
                contact.append({"type": "leader", "label": label, "value": term[key], "color": "dendrite_violet"})
        if contact:
            lines.append({"type": "blank"})
            lines.append({"type": "section", "text": "Contact"})
            lines.extend(contact)

        # --- github stats ---
        lines.append({"type": "blank"})
        lines.append({"type": "section", "text": "GitHub Stats"})
        repos_val = str(s.get("repos", 0))
        if s.get("contributed"):
            repos_val += f"  {{Contributed: {s['contributed']}}}"
        lines.append({"type": "leader", "label": "Repos", "value": repos_val})
        lines.append({"type": "leader", "label": "Stars", "value": format_number(s.get("stars", 0)), "color": "axon_amber"})
        lines.append({"type": "leader", "label": "Commits", "value": format_number(s.get("commits", 0))})
        if s.get("followers") is not None:
            lines.append({"type": "leader", "label": "Followers", "value": format_number(s.get("followers", 0))})
        lines.append({"type": "leader", "label": "PRs / Issues", "value": f"{s.get('prs', 0)} / {s.get('issues', 0)}"})
        if s.get("loc_added") is not None:
            lines.append({
                "type": "loc",
                "label": "Lines of Code",
                "total": f"{s.get('loc_added', 0) + s.get('loc_removed', 0):,}",
                "added": f"{s.get('loc_added', 0):,}",
                "removed": f"{s.get('loc_removed', 0):,}",
            })

        return {
            "handle": f"{username}@github",
            "art": self._ascii_art(term.get("ascii")),
            "lines": lines,
        }

    @staticmethod
    def _ascii_art(raw) -> list:
        """Split a config ascii block into lines; fall back to a galaxy motif."""
        if raw and str(raw).strip():
            return [ln for ln in str(raw).rstrip("\n").split("\n")]
        return [
            "        .  *   .  ",
            "     *   ,-'''-.   ",
            "   .    /  * *  \\  *",
            "      :  *  .  *  : ",
            "   *   \\   *  .  /   ",
            "     .  `-.___.-'  * ",
            "        *   .   .   ",
        ]

    def _top_langs(self, limit: int = 4, max_chars: int = 36) -> str:
        """Top languages by byte count, capped so the line fits on the card."""
        exclude = set(self.config.get("languages", {}).get("exclude", []))
        ranked = sorted(
            ((k, v) for k, v in self.languages.items() if k not in exclude),
            key=lambda kv: kv[1],
            reverse=True,
        )
        names = [name for name, _ in ranked[:limit]]
        out = []
        for name in names:
            candidate = ", ".join(out + [name])
            if len(candidate) > max_chars:
                break
            out.append(name)
        return ", ".join(out) if out else "polyglot"

    def _uptime(self, born) -> str:
        """Human 'years, months' since an ISO born date (config.terminal.born)."""
        if not born:
            return "always online"
        try:
            start = datetime.strptime(str(born), "%Y-%m-%d").date()
        except ValueError:
            return "always online"
        today = date.today()
        months = (today.year - start.year) * 12 + (today.month - start.month)
        if today.day < start.day:
            months -= 1
        years, months = divmod(max(months, 0), 12)
        parts = []
        if years:
            parts.append(f"{years} year{'s' if years != 1 else ''}")
        parts.append(f"{months} month{'s' if months != 1 else ''}")
        return ", ".join(parts)
