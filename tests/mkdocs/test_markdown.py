"""Regression tests for Markdown examples and list block ownership."""

import importlib.util
import unittest
from pathlib import Path
from xml.etree import ElementTree

import markdown


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "mkdocs_markdown", ROOT / "scripts/mkdocs_markdown.py"
)
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class MarkdownHookTests(unittest.TestCase):
    def render(self, source):
        converted = HOOK.on_page_markdown(source)
        html = markdown.markdown(
            converted, extensions=["admonition", "pymdownx.superfences"]
        )
        return ElementTree.fromstring(f"<article>{html}</article>")

    def test_fenced_alert_examples_remain_literal(self):
        for fence in ("```", "~~~", "````", "~~~~"):
            with self.subTest(fence=fence):
                example = f"{fence}markdown\n> [!NOTE]\n> Literal alert.\n{fence}"
                source = example + "\n\n> [!TIP]\n> Live alert."
                converted = HOOK.on_page_markdown(source)
                self.assertIn(example, converted)
                page = self.render(source)
                code = page.find(".//code")
                self.assertIn("> [!NOTE]\n> Literal alert.", "".join(code.itertext()))
                self.assertEqual(len(page.findall("./div[@class='admonition tip']")), 1)
                self.assertIsNone(page.find(".//div[@class='admonition note']"))

    def test_shorter_or_mismatched_fences_do_not_end_example(self):
        for inner in ("```", "~~~", "````not-a-closer"):
            with self.subTest(inner=inner):
                source = f"````markdown\n{inner}\n> [!NOTE]\n> Literal.\n````"
                self.assertEqual(HOOK.on_page_markdown(source), source)

    def test_list_nested_fenced_alert_example(self):
        source = (
            "- Examples\n\n"
            "  ```markdown\n"
            "  > [!NOTE]\n"
            "  > Literal alert.\n"
            "  ```\n\n"
            "  > [!TIP]\n"
            "  > Live alert."
        )
        page = self.render(source)
        item = page.find("./ul/li")
        self.assertIn("> [!NOTE]", "".join(item.find(".//code").itertext()))
        self.assertIsNotNone(item.find("./div[@class='admonition tip']"))
        self.assertIsNone(item.find(".//div[@class='admonition note']"))

    def test_peer_blockquotes_stay_outside_nested_list(self):
        for quote in ("> Peer quote.", "> [!NOTE]\n    > Peer note."):
            with self.subTest(quote=quote):
                source = f"1. Step\n\n    - Child\n\n    {quote}"
                step = self.render(source).find("./ol/li")
                child = step.find("./ul/li")
                self.assertEqual("".join(child.itertext()).strip(), "Child")
                self.assertEqual(len(step), 3)
                self.assertIn(step[2].tag, ("blockquote", "div"))

    def test_shallower_blockquotes_end_list_continuations(self):
        source = "1. Step\n\n    - Child\n\n> [!NOTE]\n> Outside."
        page = self.render(source)
        self.assertIsNotNone(page.find("./div[@class='admonition note']"))
        self.assertIsNone(page.find("./ol//div[@class='admonition note']"))

    def test_deeper_blockquotes_remain_list_children(self):
        source = "1. Step\n\n    - Child\n\n      > [!NOTE]\n      > Nested."
        page = self.render(source)
        self.assertIsNotNone(page.find("./ol/li/ul/li/div[@class='admonition note']"))


if __name__ == "__main__":
    unittest.main()
