"""Regression checks: python -B scripts/test_validate_tm7.py (standard library only)."""
from pathlib import Path
import os
import re
import tempfile
import unittest

from validate_tm7 import validate, read_xml, signature, N, I

SKILL = Path(__file__).resolve().parents[1]
BLANK = SKILL / 'assets/example-minimal.tm7'
WORKED = SKILL / 'references/core-worked-example.tm7'
POPULATED = SKILL / 'references/Example_Threat_Model.tm7'


class CoreConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worked = WORKED.read_text(encoding='utf-8')

    def reject(self, content, message):
        self.assertTrue(content != self.worked, 'Mutation did not alter the fixture')
        with tempfile.TemporaryDirectory(dir=os.environ.get('TM7_TEST_TMP')) as folder:
            path = Path(folder) / 'broken.tm7'
            path.write_text(content, encoding='utf-8')
            errors, _ = validate(path, BLANK)
            self.assertTrue(any(message in x for x in errors), errors)

    def test_valid_assets(self):
        for path, template, counts in ((BLANK, BLANK, (0, 0, 0)),
                                       (WORKED, BLANK, (2, 1, 1)),
                                       (POPULATED, BLANK, (10, 10, 50))):
            with self.subTest(path=path.name):
                errors, result = validate(path, template)
                self.assertEqual(errors, [])
                self.assertEqual(tuple(result[x] for x in ('borders', 'connectors', 'threats')), counts)

    def test_duplicate_serializer_id(self):
        self.reject(self.worked.replace('z:Id="i4"', 'z:Id="i3"', 1), 'Duplicate z:Id')

    def test_unbound_qname(self):
        self.reject(self.worked.replace('i:type="b:ListDisplayAttribute"',
                                       'i:type="unbound:ListDisplayAttribute"', 1), 'Unbound i:type prefix')

    def test_wrong_member_namespace(self):
        self.reject(self.worked.replace('http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts',
                                       'urn:wrong-abstracts', 1), 'Drawing surface member order/namespace mismatch')

    def test_missing_port_member(self):
        self.reject(re.sub(r'<PortSource(?:\s[^>]*)?>East</PortSource>', '', self.worked, count=1),
                    'Connector: member order')

    def test_dangling_connector(self):
        self.reject(re.sub(r'(<SourceGuid[^>]*>)[^<]*(</SourceGuid>)',
                           r'\g<1>11111111-1111-4111-8111-111111111111\2', self.worked, count=1),
                    'Unresolved connector SourceGuid')

    def test_threat_flow_direction(self):
        self.reject(self.worked.replace('<b:SourceGuid>148ade68-5c80-40f3-8e1f-4e2cabdb5991</b:SourceGuid>',
                                        '<b:SourceGuid>cc4f292c-59f9-414c-9af4-2c631ad900de</b:SourceGuid>', 1),
                    'Threat direction disagrees')

    def test_unknown_threat_type(self):
        self.reject(self.worked.replace('<b:TypeId>S3</b:TypeId>', '<b:TypeId>TH117</b:TypeId>', 1),
                    'Unknown Core threat TypeId')

    def test_unknown_stencil_type(self):
        self.reject(re.sub(r'(<TypeId[^>]*>)GE.P(</TypeId>)',
                           r'\g<1>SE.P.TMCore.AzureAppServiceWebApp\2', self.worked, count=1),
                    'Unknown stencil/flow TypeId')

    def test_unknown_property(self):
        self.reject(self.worked.replace('<a:Key>UserThreatDescription</a:Key>',
                                        '<a:Key>PossibleMitigations</a:Key>', 1), 'Unknown Core threat properties')

    def test_invalid_list_index(self):
        self.reject(self.worked.replace('<b:SelectedIndex>1</b:SelectedIndex>',
                                        '<b:SelectedIndex>999</b:SelectedIndex>', 1), 'List selection out of range')

    def test_changed_list_values(self):
        self.reject(self.worked.replace('<a:string>Not Applicable</a:string>',
                                        '<a:string>Invented option</a:string>', 1), 'List values disagree')

    def test_priority_mismatch(self):
        self.reject(self.worked.replace('<b:Priority>High</b:Priority>',
                                        '<b:Priority>Low</b:Priority>', 1), 'Threat priority mismatch')

    def test_wrong_category(self):
        self.reject(self.worked.replace('<a:Key>UserThreatCategory</a:Key><a:Value>Spoofing</a:Value>',
                                        '<a:Key>UserThreatCategory</a:Key><a:Value>Tampering</a:Value>', 1),
                    'Threat category disagrees')

    def test_changed_catalog_version(self):
        self.reject(self.worked.replace('<a:Version>4.1.0.11</a:Version>',
                                        '<a:Version>4.1.0.9</a:Version>', 1),
                    'KnowledgeBase differs from the trusted template')

    def test_root_level_threat_metadata(self):
        self.reject(self.worked.replace('<ThreatGenerationEnabled>', '<ThreatMetaData/><ThreatGenerationEnabled>', 1),
                    'ThreatModel: member order')

    def test_xml_examples_match_worked_model(self):
        doc = (SKILL / 'references/core-xml-examples.md').read_text(encoding='utf-8')
        blocks = re.findall(r'```xml\n(.*?)\n```', doc, re.S)
        self.assertEqual(len(blocks), 5)
        _, worked, _ = read_xml(WORKED)
        expected = list(worked.findall('.//a:KeyValueOfguidanyType', N))
        list_property = next(x for x in worked.findall('.//m:Lines/a:KeyValueOfguidanyType/a:Value/d:Properties/a:anyType', N)
                             if x.get('{' + I + '}type') == 'b:ListDisplayAttribute')
        expected += [list_property, worked.find('m:ThreatInstances/a:KeyValueOfstringThreatpc_P0_PhOB', N)]

        def strip_formatting(element):
            if element.text and not element.text.strip():
                element.text = None
            for child in element:
                strip_formatting(child)
                if child.tail and not child.tail.strip():
                    child.tail = None
            return element

        with tempfile.TemporaryDirectory(dir=os.environ.get('TM7_TEST_TMP')) as folder:
            for i, (block, original) in enumerate(zip(blocks, expected)):
                path = Path(folder) / f'snippet-{i}.xml'
                path.write_text(block, encoding='utf-8')
                _, parsed, scopes = read_xml(path)
                for element in parsed.iter():
                    value = element.get('{' + I + '}type')
                    if value:
                        prefix = value.split(':')[0] if ':' in value else ''
                        self.assertIn(prefix, scopes[id(element)])
                self.assertEqual(signature(strip_formatting(parsed)), signature(strip_formatting(original)))


if __name__ == '__main__':
    unittest.main()
