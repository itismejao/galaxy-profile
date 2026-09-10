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
        """Assemble neofetch-style rows from config + fetched stats/languages."""
        profile = self.config.get("profile", {})
        term = self.config.get("terminal", {})
        username = self.config["username"]

        rows = [
            {"label": "uptime:", "value": self._uptime(term.get("born")), "color": "text_bright"},
            {"label": "os:", "value": term.get("os", "GalaxyOS ✦ rolling"), "color": "text_bright"},
            {"label": "host:", "value": profile.get("location", "Earth"), "color": "text_bright"},
            {"label": "role:", "value": profile.get("tagline", "Software Engineer"), "color": "synapse_cyan"},
            {"label": "repos:", "value": str(self.stats.get("repos", 0)), "color": "dendrite_violet"},
            {"label": "commits:", "value": format_number(self.stats.get("commits", 0)), "color": "synapse_cyan"},
            {"label": "stars:", "value": format_number(self.stats.get("stars", 0)), "color": "axon_amber"},
            {"label": "prs/issues:", "value": f"{self.stats.get('prs', 0)} / {self.stats.get('issues', 0)}", "color": "text_bright"},
            {"label": "langs:", "value": self._top_langs(), "color": "text_dim"},
        ]

        return {
            "handle": f"{username}@github",
            "prompt": term.get("prompt", "neofetch --ascii"),
            "rows": rows,
        }

    def _top_langs(self, limit: int = 4) -> str:
        """Top languages by byte count, respecting the languages.exclude list."""
        exclude = set(self.config.get("languages", {}).get("exclude", []))
        ranked = sorted(
            ((k, v) for k, v in self.languages.items() if k not in exclude),
            key=lambda kv: kv[1],
            reverse=True,
        )
        names = [name for name, _ in ranked[:limit]]
        return " · ".join(names) if names else "polyglot"

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
