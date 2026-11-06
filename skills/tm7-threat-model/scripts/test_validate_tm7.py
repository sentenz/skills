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

    def test_populated_flow_labels_and_geometry(self):
        _, model, _ = read_xml(POPULATED)
        def value(element, member):
            return element.findtext('d:' + member, namespaces=N)
        def label(element):
            return next(p.findtext('k:Value', namespaces=N)
                        for p in element.findall('d:Properties/a:anyType', N)
                        if p.findtext('k:DisplayName', namespaces=N) == 'Name')
        stencils = {value(v, 'Guid'): v for v in model.findall(
            './/m:Borders/a:KeyValueOfguidanyType/a:Value', N)}
        flows = {value(v, 'Guid'): v for v in model.findall(
            './/m:Lines/a:KeyValueOfguidanyType/a:Value', N)}
        for flow in flows.values():
            source, target = (stencils[value(flow, end + 'Guid')] for end in ('Source', 'Target'))
            self.assertTrue(label(flow).startswith(label(source) + ' to ' + label(target) + ' via '))
            self.assertIn(' (', label(flow))
            for end, stencil in (('Source', source), ('Target', target)):
                self.assertEqual((value(stencil, 'Width'), value(stencil, 'Height')), ('100', '100'))
                x, y = int(value(flow, end + 'X')), int(value(flow, end + 'Y'))
                left, top = int(value(stencil, 'Left')), int(value(stencil, 'Top'))
                self.assertTrue(left <= x <= left + 100 and top <= y <= top + 100)
        for threat in model.findall('m:ThreatInstances/a:KeyValueOfstringThreatpc_P0_PhOB/a:Value', N):
            props = {p.findtext('a:Key', namespaces=N): p.findtext('a:Value', namespaces=N)
                     for p in threat.findall('k:Properties/a:KeyValueOfstringstring', N)}
            self.assertEqual(props['InteractionString'],
                             label(flows[threat.findtext('k:FlowGuid', namespaces=N)]))

    def test_populated_preserves_supplied_export_geometry(self):
        # Compatibility baseline: the supplied populated TMT export, before layout expansion.
        _, model, _ = read_xml(POPULATED)
        expected = {
            'eb7fcab6-6c6f-4057-805e-8263102d5a6e': ('13', '181', '100', '100'),
            '1cd50465-88c8-4d5a-9fe8-86ba82b78968': ('369', '10', '820', '675'),
            'b12efa5e-d565-4d97-970c-0f16f0efcdbe': ('591', '182', '100', '100'),
            '68f7ea80-2b40-443c-97d0-8afdb8fb9f5b': ('590', '495', '100', '100'),
            'cea9ef0a-d9bd-46c5-8c96-6dbce2b58a07': ('955', '107', '100', '100'),
            '2c04f557-30f1-4fde-9527-2b190e6b2d7c': ('11', '323', '100', '100'),
            '5f4312a0-1972-49c0-adf1-b7207b1aee33': ('13', '58', '100', '100'),
            '6bd55692-9166-48ab-a7ab-45815087d674': ('1311', '396', '100', '100'),
            'fafd48d9-90dd-4e9c-8daf-bf2efb3ac46a': ('1313', '105', '100', '100'),
            '71c124e0-039b-4be4-8f31-32192932da6b': ('934', '10', '496', '674'),
        }
        fields = ('Left', 'Top', 'Width', 'Height')
        actual = {v.findtext('d:Guid', namespaces=N):
                  tuple(v.findtext('d:' + k, namespaces=N) for k in fields)
                  for v in model.findall('.//m:Borders/a:KeyValueOfguidanyType/a:Value', N)}
        self.assertEqual(actual, expected)
        expected = {
            '9d4afcea-3e67-4aa2-abf9-4e4514946c6b': ('455', '232', 'West', 'East', '596', '232', '108', '231'),
            '552b907e-0d26-4e70-92c9-e0b4df52e9bf': ('272', '231', 'East', 'West', '108', '231', '596', '232'),
            '3ea05cdd-2a10-419e-a3df-a0bc3bf98680': ('320', '146', 'East', 'NorthWest', '108', '108', '609', '200'),
            '1dd4151c-3b0f-414b-8d77-e92441b51b47': ('1052', '376', 'West', 'SouthEast', '1316', '446', '672', '263'),
            '9ac0f863-3849-4fe2-befd-fa32dce6fea1': ('454', '298', 'East', 'SouthWest', '106', '373', '609', '263'),
            'fe9683fb-3eaf-4898-b9c6-2fd1aab24dc7': ('827', '177', 'West', 'NorthEast', '960', '157', '672', '200'),
            '3f4ff8e3-29b3-4d50-988f-590b63a01bb3': ('640', '387', 'South', 'North', '641', '277', '640', '500'),
            '55ff5bd2-fdb9-4e83-b229-0744938845fb': ('303', '331', 'SouthWest', 'East', '609', '263', '106', '373'),
            'fdfd398d-f6d8-4fb4-a772-d0d15168e4a9': ('641', '354', 'North', 'South', '640', '500', '641', '277'),
            'cb59d018-06d7-4803-9217-f168963da421': ('1179', '156', 'East', 'West', '1050', '157', '1318', '155'),
        }
        fields = ('HandleX', 'HandleY', 'PortSource', 'PortTarget', 'SourceX', 'SourceY', 'TargetX', 'TargetY')
        actual = {v.findtext('d:Guid', namespaces=N):
                  tuple(v.findtext('d:' + k, namespaces=N) for k in fields)
                  for v in model.findall('.//m:Lines/a:KeyValueOfguidanyType/a:Value', N)}
        self.assertEqual(actual, expected)

    def test_canvas_envelope_rejects_expanded_coordinates(self):
        for member, number in (('Left', '6200'), ('Top', '5000'), ('Width', '2800'), ('Height', '5250')):
            with self.subTest(member=member):
                self.reject(re.sub(r'(<'+member+r'[^>]*>)[^<]+',
                                   lambda m: m[1] + number, self.worked, count=1),
                            'Border outside bundled canvas envelope')
        for member in ('SourceX', 'SourceY', 'TargetX', 'TargetY', 'HandleX', 'HandleY'):
            with self.subTest(member=member):
                self.reject(re.sub(r'(<'+member+r'[^>]*>)[^<]+',
                                   lambda m: m[1] + '6200', self.worked, count=1),
                            'Connector outside bundled canvas envelope')

    def test_cra_scope_inventory_and_uncertainties(self):
        _, model, _ = read_xml(POPULATED)
        objects = model.findall('.//m:Borders/a:KeyValueOfguidanyType/a:Value', N)
        objects += model.findall('.//m:Lines/a:KeyValueOfguidanyType/a:Value', N)
        guids = {v.findtext('d:Guid', namespaces=N) for v in objects}
        assessment = model.findtext('m:MetaInformation/m:Assumptions', namespaces=N)
        document = (SKILL / 'references/cra-scope-assessment.md').read_text(encoding='utf-8')
        pattern = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
        self.assertEqual(set(re.findall(pattern, assessment)), guids)
        self.assertEqual(set(re.findall(pattern, document)), guids)
        unresolved = {'cea9ef0a-d9bd-46c5-8c96-6dbce2b58a07',
                      'fe9683fb-3eaf-4898-b9c6-2fd1aab24dc7',
                      '5f4312a0-1972-49c0-adf1-b7207b1aee33'}
        for v in objects:
            props = {p.findtext('k:DisplayName', namespaces=N): p.findtext('k:Value', namespaces=N)
                     for p in v.findall('d:Properties/a:anyType', N)}
            if v.findtext('d:GenericTypeId', namespaces=N) == 'GE.TB.B':
                self.assertNotIn('Out Of Scope', props)
            if props.get('Out Of Scope') == 'true':
                self.assertTrue(props.get('Reason For Out Of Scope'))
            if v.findtext('d:Guid', namespaces=N) in unresolved:
                self.assertEqual(props['Out Of Scope'], 'false')

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
        # Exact connection geometry from the supplied TMT example, independent of UUIDs.
        _, worked, _ = read_xml(WORKED)
        request, response = worked.findall('.//m:Lines/a:KeyValueOfguidanyType/a:Value', N)
        members = ('PortSource', 'PortTarget', 'SourceX', 'SourceY',
                   'TargetX', 'TargetY', 'HandleX', 'HandleY')
        expected = (('East', 'West', '195', '150', '905', '150', '563', '123'),
                    ('West', 'East', '905', '150', '195', '150', '562', '178'))
        for flow, geometry in zip((request, response), expected):
            self.assertEqual(tuple(flow.findtext('d:' + k, namespaces=N) for k in members), geometry)

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
