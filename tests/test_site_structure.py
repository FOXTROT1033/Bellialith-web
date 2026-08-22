import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SiteStructureTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding="utf-8")

    def test_internal_pages_share_one_non_fixed_header(self):
        for name in ("index.html", "features.html", "commands.html", "updates.html", "privacy.html", "terms.html"):
            html = self.read(name)
            self.assertIn('<header class="site-header">', html, name)
            self.assertNotIn('<header class="navbar">', html, name)
            self.assertIn('class="site-nav"', html, name)
            self.assertIn('class="nav-dashboard"', html, name)
            self.assertIn('class="nav-logout"', html, name)

        css = self.read("style.css")
        self.assertNotRegex(css, r"\.site-header\s*\{[^}]*position\s*:\s*(fixed|sticky)", re.S)
        self.assertNotRegex(css, r"\.navbar\s*\{[^}]*position\s*:\s*(fixed|sticky)", re.S)

    def test_global_links_never_fall_back_to_browser_purple(self):
        css = self.read("style.css")
        self.assertIn("a:visited", css)
        self.assertIn("color: inherit", css)
        self.assertNotIn("color: purple", css.lower())

    def test_commands_page_uses_documentation_grid(self):
        html = self.read("commands.html")
        self.assertGreaterEqual(html.count('class="command-section"'), 4)
        self.assertGreaterEqual(html.count('class="command-grid"'), 4)
        self.assertGreaterEqual(html.count('class="command-card"'), 10)
        self.assertIn('class="docs-page"', html)
        self.assertIn('class="page-hero"', html)

    def test_updates_page_uses_update_cards(self):
        html = self.read("updates.html")
        self.assertIn('class="updates-grid"', html)
        self.assertGreaterEqual(html.count('class="update-card"'), 4)
        self.assertIn('class="updates-cta"', html)

    def test_login_page_has_auth_only_header(self):
        html = self.read("login.html")
        self.assertIn('class="site-header auth-header"', html)
        self.assertNotIn('class="site-nav"', html)
        self.assertNotIn('href="/features"', html)
        self.assertNotIn('href="/commands"', html)
        self.assertNotIn('href="/updates"', html)


if __name__ == "__main__":
    unittest.main()
