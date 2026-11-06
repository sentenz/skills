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
                                       (WORKED, BLANK, (2, 2, 1)),
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
        self.reject(re.sub(r'<PortSource(?:\s[^>]*)?>[^<]+</PortSource>', '', self.worked, count=1),
                    'Connector: member order')

    def test_dangling_connector(self):
        self.reject(re.sub(r'(<SourceGuid[^>]*>)[^<]*(</SourceGuid>)',
                           r'\g<1>11111111-1111-4111-8111-111111111111\2', self.worked, count=1),
                    'Unresolved connector SourceGuid')

    def test_threat_flow_direction(self):
        self.reject(self.worked.replace('<b:SourceGuid>148ade68-5c80-40f3-8e1f-4e2cabdb5991</b:SourceGuid>',
                                        '<b:SourceGuid>cc4f292c-59f9-414c-9af4-2c631ad900de</b:SourceGuid>', 1),
                    'Threat direction disagrees')

    def test_request_response_connection(self):
        _, worked, _ = read_xml(WORKED)
        request, response = worked.findall('.//m:Lines/a:KeyValueOfguidanyType/a:Value', N)
        self.assertNotEqual(request.findtext('d:Guid', namespaces=N),
                            response.findtext('d:Guid', namespaces=N))
        self.assertEqual(request.findtext('d:SourceGuid', namespaces=N),
                         response.findtext('d:TargetGuid', namespaces=N))
        self.assertEqual(request.findtext('d:TargetGuid', namespaces=N),
                         response.findtext('d:SourceGuid', namespaces=N))
        labels = []
        for flow, direction, endpoints in ((request, 'request', 'Client to Service'),
                                           (response, 'response', 'Service to Client')):
            props = flow.findall('d:Properties/a:anyType', N)
            label = next(p.findtext('k:Value', namespaces=N) for p in props
                         if p.findtext('k:DisplayName', namespaces=N) == 'Name')
            self.assertTrue(label.startswith(endpoints + ' via '), label)
            self.assertIn(' ' + direction + ' (', label)
            labels.append(label)
            for p in props:
                if p.findtext('k:Name', namespaces=N) in (
                        'authenticatesSource', 'authenticatesDestination',
                        'providesConfidentiality', 'providesIntegrity'):
                    values = p.findall('k:Value/a:string', N)
                    self.assertEqual(values[int(p.findtext('k:SelectedIndex', namespaces=N))].text, 'No')
        threat = worked.find('m:ThreatInstances/a:KeyValueOfstringThreatpc_P0_PhOB/a:Value', N)
        props = {p.findtext('a:Key', namespaces=N): p.findtext('a:Value', namespaces=N)
                 for p in threat.findall('k:Properties/a:KeyValueOfstringstring', N)}
        self.assertEqual(props['InteractionString'], labels[0])
        self.assertEqual(threat.findtext('k:FlowGuid', namespaces=N),
                         request.findtext('d:Guid', namespaces=N))

    def test_request_response_geometry(self):
        _, worked, _ = read_xml(WORKED)
        flows = worked.findall('.//m:Lines/a:KeyValueOfguidanyType/a:Value', N)
        for flow, direction in zip(flows, ('request', 'response')):
            def number(name):
                return float(flow.findtext('d:' + name, namespaces=N))
            sx, sy, tx, ty = (number(x) for x in ('SourceX', 'SourceY', 'TargetX', 'TargetY'))
            self.assertAlmostEqual(number('HandleX'), (sx + tx) / 2)
            self.assertAlmostEqual(number('HandleY'), (sy + ty) / 2)
            if direction == 'request':
                self.assertEqual((sx, sy), (150, 100))
                self.assertLess(max(sy, ty), 150)
                self.assertEqual(flow.findtext('d:PortSource', namespaces=N), 'North')
                self.assertEqual(flow.findtext('d:PortTarget', namespaces=N), 'North')
                cx, cy = tx, ty
            else:
                self.assertEqual((tx, ty), (150, 200))
                self.assertGreater(min(sy, ty), 150)
                self.assertEqual(flow.findtext('d:PortSource', namespaces=N), 'South')
                self.assertEqual(flow.findtext('d:PortTarget', namespaces=N), 'South')
                cx, cy = sx, sy
            self.assertAlmostEqual((cx - 950) ** 2 + (cy - 150) ** 2, 50 ** 2, places=4)

    def test_fractional_connector_coordinates(self):
        for coordinate in ('HandleX', 'HandleY', 'SourceX', 'SourceY', 'TargetX', 'TargetY'):
            for invalid in ('557.3223305', '550.0', '5.5e2'):
                with self.subTest(coordinate=coordinate, value=invalid):
                    self.reject(re.sub(r'(<'+coordinate+r'[^>]*>)[^<]+',
                                       lambda m: m[1] + invalid, self.worked, count=1),
                                'Connector coordinate must be an integer: ' + coordinate)

    def test_request_threat_cannot_reference_response(self):
        self.reject(self.worked.replace(
            '<b:FlowGuid>6cae5818-d775-4935-96a4-b317b1fcdecb</b:FlowGuid>',
            '<b:FlowGuid>7bb5aad7-8c3f-4c99-a2e8-9344102f61b5</b:FlowGuid>', 1),
            'Threat direction disagrees')

    def test_one_way_flow_remains_valid(self):
        content, count = re.subn(
            r'<a:KeyValueOfguidanyType><a:Key>7bb5aad7-8c3f-4c99-a2e8-9344102f61b5</a:Key>'
            r'.*?</a:KeyValueOfguidanyType>', '', self.worked, count=1, flags=re.S)
        self.assertEqual(count, 1)
        with tempfile.TemporaryDirectory(dir=os.environ.get('TM7_TEST_TMP')) as folder:
            path = Path(folder) / 'one-way.tm7'
            path.write_text(content, encoding='utf-8')
            errors, result = validate(path, BLANK)
            self.assertEqual(errors, [])
            self.assertEqual(result['connectors'], 1)

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
        self.assertEqual(len(blocks), 6)
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
