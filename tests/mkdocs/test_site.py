"""Integration tests for SKILL.md-only publication and repository links."""

import json
import tempfile
import unittest
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import Abort


ROOT = Path(__file__).resolve().parents[2]


class SkillSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.write("docs/README.md", "# Must not be published\n")
        self.write("skills/README.md", "# Must not be published\n")
        self.write("skills/example/references/guide.md", "# Guide\n")
        self.write("skills/example/scripts/check.py", "print('not published')\n")
        self.write("skills/example/assets/data.json", "{}\n")
        self.write("skills/other/SKILL.md", "---\nname: other\n---\n# Other\n")
        self.write("skills/example/SKILL.md", """---
name: example
description: An example skill.
metadata:
  version: '1.0'
---
# Example

[Guide](references/guide.md#guide)
[Script](scripts/check.py)
[Asset](assets/data.json)
[Other](../other/SKILL.md#other)
[External](https://example.com/path?q=1#anchor)
[Reference link][guide]

[guide]: references/guide.md?plain=1#guide

`[Literal](references/guide.md)`

```markdown
[Example code](references/guide.md)
```

> [!NOTE]
> An alert.
""")
        self.write("mkdocs.yml", f"""site_name: Test Skills
site_description: Test catalog.
site_url: https://example.com/skills/
repo_url: https://github.com/sentenz/skills
edit_uri: edit/main/
docs_dir: docs
site_dir: public
strict: true
extra:
  source_ref: main
hooks:
  - {ROOT / 'scripts/mkdocs_markdown.py'}
  - {ROOT / 'scripts/mkdocs_skills.py'}
markdown_extensions:
  - admonition
  - pymdownx.superfences
""")
        self.config = load_config(config_file=str(self.root / "mkdocs.yml"))

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_only_skills_are_published_and_indexed(self):
        build(self.config)
        output = self.root / "public"
        pages = {path.relative_to(output).as_posix() for path in output.rglob("*.html")}
        self.assertEqual(pages, {
            "index.html", "404.html", "skills/example/SKILL/index.html",
            "skills/other/SKILL/index.html",
        })
        self.assertFalse((output / "skills/example/references").exists())
        self.assertFalse((output / "skills/example/scripts").exists())
        self.assertFalse((output / "skills/example/assets").exists())
        index = json.loads((output / "search/search_index.json").read_text())
        for document in index["docs"]:
            self.assertIn(document["location"].split("#")[0], {
                "", "skills/example/SKILL/", "skills/other/SKILL/",
            })

        page = (output / "skills/example/SKILL/index.html").read_text()
        base = "https://github.com/sentenz/skills/blob/main/skills/example/"
        self.assertIn(base + 'references/guide.md#guide"', page)
        self.assertIn(base + 'references/guide.md?plain=1#guide"', page)
        self.assertIn(base + 'scripts/check.py"', page)
        self.assertIn(base + 'assets/data.json"', page)
        self.assertIn('href="../../other/SKILL/#other"', page)
        self.assertIn('href="https://example.com/path?q=1#anchor"', page)
        self.assertIn('<code>[Literal](references/guide.md)</code>', page)
        self.assertIn('references/guide.md)', page)
        self.assertIn('class="admonition note"', page)
        self.assertIn('https://github.com/sentenz/skills/edit/main/skills/example/SKILL.md', page)
        self.assertNotIn('metadata:', page)

        # Reuse config as mkdocs serve does: discovery and navigation must refresh.
        (self.root / "skills/other/SKILL.md").unlink()
        self.write("skills/example/SKILL.md", "# Example\n")
        self.write("skills/new/SKILL.md", "# New\n")
        build(self.config)
        self.assertFalse((output / "skills/other/SKILL/index.html").exists())
        self.assertTrue((output / "skills/new/SKILL/index.html").exists())
        home = (output / "index.html").read_text()
        self.assertIn('skills/new/SKILL/', home)
        self.assertNotIn('skills/other/SKILL/', home)

    def test_missing_reference_fails_strict_build(self):
        self.write("skills/example/SKILL.md", "# Example\n\n[Missing](references/missing.md)\n")
        with self.assertLogs("mkdocs", level="WARNING"):
            with self.assertRaises(Abort):
                build(self.config)


if __name__ == "__main__":
    unittest.main()
