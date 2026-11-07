"""CLI regression tests for the imported draw.io utilities."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


SKILL = Path(__file__).resolve().parents[2] / 'skills/draw-io-diagram-generator'


class DrawioScriptTests(unittest.TestCase):
    def run_script(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SKILL / 'scripts' / script), *map(str, args)],
            capture_output=True, text=True,
        )

    def test_templates_validate(self):
        templates = sorted((SKILL / 'assets/templates').glob('*.drawio'))
        self.assertEqual(len(templates), 5)
        for template in templates:
            with self.subTest(template=template.name):
                result = self.run_script('validate-drawio.py', template)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsupported_and_invalid_xml_fail(self):
        for content in (
            '<mxfile><diagram id="compressed">encoded-data</diagram></mxfile>',
            '<mxfile><diagram',
            '<mxfile><diagram id="empty"><mxGraphModel><root/></mxGraphModel></diagram></mxfile>',
        ):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'invalid.drawio'
                path.write_text(content)
                result = self.run_script('validate-drawio.py', path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertNotIn('PASS', result.stdout)

    def test_insert_dry_run_and_page_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'diagram.drawio'
            tree = ET.parse(SKILL / 'assets/templates/flowchart.drawio')
            second = ET.parse(SKILL / 'assets/templates/architecture.drawio').getroot()[0]
            second.set('id', 'second-page')
            tree.getroot().append(second)
            tree.write(path)
            original = path.read_bytes()
            args = (path, 'API & worker <queue>', 200, 300)
            for index in (-1, 2):
                result = self.run_script('add-shape.py', *args, '--diagram-index', index)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(path.read_bytes(), original)
            result = self.run_script('add-shape.py', *args, '--dry-run')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(path.read_bytes(), original)
            result = self.run_script('add-shape.py', *args, '--diagram-index', 1)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            pages = ET.parse(path).getroot().findall('diagram')
            self.assertEqual(
                ET.canonicalize(ET.tostring(pages[0], encoding='unicode'), strip_text=True),
                ET.canonicalize(ET.tostring(tree.getroot()[0], encoding='unicode'), strip_text=True),
            )
            cells = pages[1].find('mxGraphModel/root').findall('mxCell')
            self.assertEqual(cells[-1].get('value'), args[1])
            result = self.run_script('validate-drawio.py', path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
