"""Integration tests for SKILL.md-only publication and repository links."""

import json
import tempfile
import shutil
import subprocess
import sys
import tomllib
import socket
import time
from urllib.error import URLError
from urllib.request import urlopen

import tomli_w
import unittest
from pathlib import Path



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
        self.write("skills/example/assets/diagram.svg", "<svg/>\n")
        self.write("skills/example/references/café guide.md", "# Unicode\n")
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
[Directory](references/)
[Unicode](references/caf%C3%A9%20guide.md?plain=1#unicode)
![Diagram](assets/diagram.svg)
![Referenced diagram][diagram]
[Diagram source][diagram]

[guide]: references/guide.md?plain=1#guide
[diagram]: assets/diagram.svg "Diagram title"

`[Literal](references/guide.md)`

```markdown
[Example code](references/guide.md)
```

> [!NOTE]
> An alert.
""")
        config = tomllib.loads((ROOT / "zensical.toml").read_text())
        config["project"]["site_name"] = "Test Skills"
        config["project"]["site_description"] = "Test catalog."
        config["project"]["site_url"] = "https://example.com/skills/"
        self.write("zensical.toml", tomli_w.dumps(config))
        shutil.copytree(ROOT / "docs/assets", self.root / "docs/assets")

    def build(self, *, success=True):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/docs.py"), "build"],
            cwd=self.root, capture_output=True, text=True, timeout=60,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_only_skills_are_published_and_indexed(self):
        self.build()
        output = self.root / "public"
        pages = {path.relative_to(output).as_posix() for path in output.rglob("*.html")}
        self.assertEqual(pages, {
            "index.html", "404.html", "skills/example/SKILL/index.html",
            "skills/other/SKILL/index.html",
        })
        self.assertFalse((output / "skills/example/references").exists())
        self.assertFalse((output / "skills/example/scripts").exists())
        self.assertFalse((output / "skills/example/assets").exists())
        index = json.loads((output / "search.json").read_text())
        for document in index["items"]:
            self.assertIn(document["location"].split("#")[0], {
                "", "skills/example/SKILL/", "skills/other/SKILL/",
            })

        page = (output / "skills/example/SKILL/index.html").read_text()
        base = "https://github.com/sentenz/skills/blob/main/skills/example/"
        self.assertIn(base + 'references/guide.md#guide"', page)
        self.assertIn(base + 'references/guide.md?plain=1#guide"', page)
        self.assertIn(base + 'scripts/check.py"', page)
        self.assertIn(base + 'assets/data.json"', page)
        self.assertIn(base + 'references/caf%C3%A9%20guide.md?plain=1#unicode"', page)
        self.assertIn('https://github.com/sentenz/skills/tree/main/skills/example/references"', page)
        self.assertEqual(page.count('src="https://github.com/sentenz/skills/raw/main/skills/example/assets/diagram.svg"'), 2)
        self.assertIn(base + 'assets/diagram.svg"', page)
        self.assertIn('title="Diagram title"', page)
        self.assertIn('href="../../other/SKILL/#other"', page)
        self.assertIn('href="https://example.com/path?q=1#anchor"', page)
        self.assertIn('<code>[Literal](references/guide.md)</code>', page)
        self.assertIn('references/guide.md)', page)
        self.assertIn('class="admonition note"', page)
        self.assertIn('https://github.com/sentenz/skills/edit/main/skills/example/SKILL.md', page)
        self.assertNotIn('metadata:', page)
        self.assertEqual(
            (output / "assets/css/style.css").read_bytes(),
            (ROOT / "docs/assets/css/style.css").read_bytes(),
        )

        # Rebuild after source changes: discovery and navigation must refresh.
        (self.root / "skills/other/SKILL.md").unlink()
        self.write("skills/example/SKILL.md", "# Example\n")
        self.write("skills/new/SKILL.md", "# New\n")
        self.build()
        self.assertFalse((output / "skills/other/SKILL/index.html").exists())
        self.assertTrue((output / "skills/new/SKILL/index.html").exists())
        home = (output / "index.html").read_text()
        self.assertIn('skills/new/SKILL/', home)
        self.assertNotIn('skills/other/SKILL/', home)

    def test_missing_reference_fails_strict_build(self):
        self.write("skills/example/SKILL.md", "# Example\n\n[Missing](references/missing.md)\n")
        output = self.build(success=False)
        self.assertIn("references/missing.md", output)

    def test_cpp_mock_lists_are_nested_in_built_html(self):
        source = (ROOT / "skills/cpp-mock-testing/SKILL.md").read_text()
        section = source.split("## 7. Style Guide", 1)[1].split("## 8. Template", 1)[0]
        self.write("skills/example/SKILL.md", "# Style Guide\n" + section)
        self.build()
        page = (self.root / "public/skills/example/SKILL/index.html").read_text()
        self.assertRegex(page, r"Expectations</p>\s*<ul>\s*<li>Use <code>EXPECT_CALL")
        self.assertRegex(page, r"Matchers and Actions</p>\s*<ul>\s*<li>Use built-in matchers")

    def test_missing_skill_fails_strict_build(self):
        self.write("skills/example/SKILL.md", "# Example\n\n[Missing](../missing/SKILL.md)\n")
        self.assertIn("missing/SKILL.md", self.build(success=False))

    def test_missing_anchor_fails_strict_build(self):
        self.write("skills/example/SKILL.md", "# Example\n\n[Other](../other/SKILL.md#absent)\n")
        self.assertIn("anchor does not exist", self.build(success=False))

    def test_no_skills_fails_build(self):
        shutil.rmtree(self.root / "skills")
        self.assertIn("No skills/**/SKILL.md files found", self.build(success=False))

    def test_preview_refreshes_catalog_and_skill_content(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        with tempfile.TemporaryFile(mode="w+") as log:
            process = subprocess.Popen(
                [sys.executable, str(ROOT / "scripts/docs.py"), "serve", "--dev-addr", f"127.0.0.1:{port}"],
                cwd=self.root, stdout=log, stderr=log,
            )
            try:
                def wait_for(path, expected, absent=None):
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline and process.poll() is None:
                        try:
                            with urlopen(f"http://127.0.0.1:{port}/skills/{path}", timeout=1) as response:
                                html = response.read().decode()
                            if expected in html and (absent is None or absent not in html):
                                return
                        except (URLError, TimeoutError):
                            pass
                        time.sleep(0.2)
                    log.seek(0)
                    self.fail(f"Preview did not update {path}: {log.read()}")

                wait_for("", "skills/other/SKILL/")
                self.write("skills/new/SKILL.md", "# Added during preview\n")
                wait_for("", "skills/new/SKILL/")
                wait_for("skills/new/SKILL/", "Added during preview")
                self.write("skills/new/SKILL.md", "# Edited during preview\n")
                wait_for("skills/new/SKILL/", "Edited during preview")
                (self.root / "skills/new/SKILL.md").unlink()
                wait_for("", "skills/other/SKILL/", absent="skills/new/SKILL/")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()



if __name__ == "__main__":
    unittest.main()
