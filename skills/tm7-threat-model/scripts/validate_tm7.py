#!/usr/bin/env python3
"""Check Core TM7 structure and references against an unchanged trusted export.

Uses only the Python standard library. This is a consistency checker for the bundled
Core exports, not a replacement for Microsoft Threat Modeling Tool deserialization.
"""
import argparse
import re
from pathlib import Path
import sys
import uuid
import xml.etree.ElementTree as ET

M = 'http://schemas.datacontract.org/2004/07/ThreatModeling.Model'
D = M + '.Abstracts'
K = 'http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase'
A = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
I = 'http://www.w3.org/2001/XMLSchema-instance'
Z = 'http://schemas.microsoft.com/2003/10/Serialization/'
X = 'http://www.w3.org/2001/XMLSchema'
N = {'m': M, 'd': D, 'k': K, 'a': A}
ROOT_MEMBERS = ['DrawingSurfaceList', 'MetaInformation', 'Notes', 'ThreatInstances',
                'ThreatGenerationEnabled', 'Validations', 'Version', 'KnowledgeBase', 'Profile']
SURFACE_MEMBERS = ['GenericTypeId', 'Guid', 'Properties', 'TypeId', 'Borders', 'Header', 'Lines', 'Zoom']
BORDER_MEMBERS = ['GenericTypeId', 'Guid', 'Properties', 'TypeId', 'Height', 'Left',
                  'StrokeDashArray', 'StrokeThickness', 'Top', 'Width']
FLOW_MEMBERS = ['GenericTypeId', 'Guid', 'Properties', 'TypeId', 'HandleX', 'HandleY',
                'PortSource', 'PortTarget', 'SourceGuid', 'SourceX', 'SourceY',
                'TargetGuid', 'TargetX', 'TargetY']
THREAT_MEMBERS = ['ChangedBy', 'DrawingSurfaceGuid', 'FlowGuid', 'Id', 'InteractionKey',
                  'InteractionString', 'ModifiedAt', 'Priority', 'Properties', 'SourceGuid',
                  'State', 'StateInformation', 'TargetGuid', 'Title', 'TypeId', 'Upgraded',
                  'UserThreatCategory', 'UserThreatDescription', 'UserThreatShortDescription', 'Wide']
SHAPES = {'GE.P': 'StencilEllipse', 'GE.EI': 'StencilRectangle', 'GE.DS': 'StencilParallelLines',
          'GE.DF': 'Connector', 'GE.TB.B': 'BorderBoundary'}
COMMON_PROPERTIES = {'Name', '71f3d9aa-b8ef-4e54-8126-607a1d903103',
                     '752473b6-52d4-4776-9a24-202153f7d579'}


def text(element, path):
    return element.findtext(path, default='', namespaces=N)


def signature(element):
    """Compare catalog content while ignoring equivalent namespace prefix spellings."""
    return (element.tag, tuple(sorted(element.attrib.items())), element.text or '',
            tuple((signature(child), child.tail or '') for child in element))


def catalog_signature(element):
    """The KB object's serializer identity is separate from its catalog content."""
    tag, attrs, content, children = signature(element)
    return tag, tuple((key, value) for key, value in attrs if key != '{' + Z + '}Id'), content, children


def read_xml(path):
    data = Path(path).read_bytes()
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('DTD/entity declarations are not part of the Core export format')
    contexts, stack, pending = {}, [], {}
    for event, value in ET.iterparse(Path(path), events=('start-ns', 'start', 'end')):
        if event == 'start-ns':
            pending[value[0]] = value[1]
        elif event == 'start':
            scope = dict(stack[-1]) if stack else {}
            scope.update(pending)
            pending.clear()
            stack.append(scope)
            contexts[id(value)] = scope
        else:
            stack.pop()
    return data, value, contexts  # Last end event is the root.


def validate(path, template):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    data, root, scopes = read_xml(path)
    _, baseline, _ = read_xml(template)

    def members(element, names, namespace, label):
        check(element is not None and [x.tag for x in element] ==
              ['{' + namespace + '}' + name for name in names], label + ': member order/namespace mismatch')

    def guid(value, label):
        try:
            check(str(uuid.UUID(value)) == value, label + ': UUID must be canonical lowercase')
        except (ValueError, AttributeError):
            check(False, label + ': invalid UUID ' + repr(value))

    resolved_types = {}
    for element in root.iter():
        value = element.get('{' + I + '}type')
        if value:
            prefix, name = value.split(':', 1) if ':' in value else ('', value)
            uri = scopes[id(element)].get(prefix)
            check(uri is not None, 'Unbound i:type prefix: ' + value)
            resolved_types[id(element)] = (uri, name)
    check(data.lstrip().startswith(b'<ThreatModel '), 'Expected ThreatModel root without XML declaration/BOM')
    check(root.tag == '{' + M + '}ThreatModel', 'Wrong root namespace')
    members(root, ROOT_MEMBERS, M, 'ThreatModel')
    members(root.find('m:MetaInformation', N), ['Assumptions', 'Contributors', 'ExternalDependencies',
            'HighLevelSystemDescription', 'Owner', 'Reviewer', 'ThreatModelName'], M, 'MetaInformation')
    check(text(root, 'm:Version') == '4.3', 'Unexpected model Version')
    check(text(root, 'm:ThreatGenerationEnabled') in ('true', 'false'), 'Invalid ThreatGenerationEnabled')
    profile = root.find('m:Profile', N)
    check(profile is not None and [x.tag for x in profile] == ['PromptedKb'],
          'Profile must contain an unqualified PromptedKb')
    kb = root.find('m:KnowledgeBase', N)
    trusted_kb = baseline.find('m:KnowledgeBase', N)
    if kb is None or trusted_kb is None:
        return errors + ['Missing KnowledgeBase in model or template'], {}
    manifest = kb.find('k:Manifest', N)
    check(manifest is not None and text(manifest, 'k:Name') == 'SDL TM Knowledge Base (Core)',
          'Expected SDL TM Knowledge Base (Core)')
    check(manifest is not None and text(manifest, 'k:Id') == 'cc62ebae-3748-431e-b1df-f4220dc9003f',
          'Unexpected Core manifest ID')
    check(catalog_signature(kb) == catalog_signature(trusted_kb), 'KnowledgeBase differs from the trusted template')
    members(kb, ['GenericElements', 'Manifest', 'StandardElements', 'ThreatCategories',
                 'ThreatMetaData', 'ThreatTypes'], K, 'KnowledgeBase')
    elements = {}
    for group in ('GenericElements', 'StandardElements'):
        for item in kb.findall('k:' + group + '/k:ElementType', N):
            key = text(item, 'k:Id')
            check(key not in elements, 'Duplicate catalog element ID: ' + key)
            elements[key] = item
    threats = {text(x, 'k:Id'): x for x in kb.findall('k:ThreatTypes/k:ThreatType', N)}
    categories = {text(x, 'k:Id'): x for x in kb.findall('k:ThreatCategories/k:ThreatCategory', N)}
    property_names = {text(x, 'm:Name') for x in kb.findall(
        'k:ThreatMetaData/m:PropertiesMetaData/m:ThreatMetaDatum', N)}

    def ancestry(type_id):
        chain = []
        while type_id != 'ROOT' and type_id in elements and type_id not in chain:
            chain.append(type_id)
            type_id = text(elements[type_id], 'k:ParentId')
        return chain

    def attributes(type_id):
        result = {}
        for key in reversed(ancestry(type_id)):
            for attr in elements[key].findall('k:Attributes/k:Attribute', N):
                result[text(attr, 'k:Name')] = attr
        return result

    ids = [x.get('{' + Z + '}Id') for x in root.iter() if x.get('{' + Z + '}Id')]
    check(len(ids) == len(set(ids)), 'Duplicate z:Id serializer identifiers')
    for item in root.iter():
        ref = item.get('{' + Z + '}Ref')
        if ref:
            check(ref in ids, 'Unresolved z:Ref: ' + ref)

    def diagram_properties(value, type_id):
        attrs = attributes(type_id)
        found = []
        props = value.find('d:Properties', N)
        check(props is not None, 'Missing diagram Properties')
        for prop in props if props is not None else []:
            check(prop.tag == '{' + A + '}anyType', 'Wrong diagram property wrapper')
            kind = resolved_types.get(id(prop))
            check(kind is not None and kind[0] == K and kind[1] in (
                'HeaderDisplayAttribute', 'StringDisplayAttribute', 'BooleanDisplayAttribute',
                'ListDisplayAttribute', 'StaticListDisplayAttribute'), 'Invalid display attribute type')
            name = text(prop, 'k:Name')
            if not name:  # Exported headers and Name display attributes have empty internal names.
                check(kind in ((K, 'HeaderDisplayAttribute'), (K, 'StringDisplayAttribute')),
                      'Unnamed non-text property')
                continue
            check(name not in found, 'Duplicate diagram property: ' + name)
            found.append(name)
            common = COMMON_PROPERTIES | ({'15ccd509-98eb-49ad-b9c2-b4a2926d1780'} if type_id in elements
                                         and any(x in ancestry(type_id) for x in ('GE.DF', 'GE.TB.B')) else set())
            check(name in attrs or name in common, 'Unknown property for ' + type_id + ': ' + name)
            val = prop.find('k:Value', N)
            if kind in ((K, 'StringDisplayAttribute'), (K, 'BooleanDisplayAttribute')):
                expected_type = 'boolean' if kind[1] == 'BooleanDisplayAttribute' else 'string'
                check(val is not None and resolved_types.get(id(val)) == (X, expected_type),
                      'Incorrect primitive property value type: ' + name)
            if kind in ((K, 'ListDisplayAttribute'), (K, 'StaticListDisplayAttribute')):
                val = prop.find('k:Value', N)
                check(val is not None and resolved_types.get(id(val)) == (A, 'ArrayOfstring'),
                      'List property must use Arrays ArrayOfstring: ' + name)
                options = [x.text or '' for x in val] if val is not None else []
                check(val is not None and all(x.tag == '{' + A + '}string' for x in val),
                      'List values must be Arrays strings: ' + name)
                if name in attrs:
                    expected = [x.text or '' for x in attrs[name].find('k:AttributeValues', N)]
                    check(options == expected, 'List values disagree with Core catalog: ' + name)
                try:
                    check(0 <= int(text(prop, 'k:SelectedIndex')) < len(options),
                          'List selection out of range: ' + name)
                except ValueError:
                    check(False, 'Invalid SelectedIndex: ' + name)
        check(set(attrs).issubset(found), 'Missing inherited configurable properties for ' + type_id)

    surfaces, objects, flows = {}, {}, {}
    all_guids = []
    for surface in root.findall('m:DrawingSurfaceList/m:DrawingSurfaceModel', N):
        expected = ['{' + D + '}' + x for x in SURFACE_MEMBERS[:4]] + [
            '{' + M + '}' + x for x in SURFACE_MEMBERS[4:]]
        check([x.tag for x in surface] == expected, 'Drawing surface member order/namespace mismatch')
        sid = text(surface, 'd:Guid')
        guid(sid, 'DrawingSurfaceGuid')
        all_guids.append(sid)
        surfaces[sid] = surface
        check(text(surface, 'd:GenericTypeId') == text(surface, 'd:TypeId') == 'DRAWINGSURFACE',
              'Drawing surface type mismatch')
        local_objects = {}
        for group in ('Borders', 'Lines'):
            container = surface.find('m:' + group, N)
            for entry in container if container is not None else []:
                members(entry, ['Key', 'Value'], A, 'Diagram dictionary entry')
                check(entry.tag == '{' + A + '}KeyValueOfguidanyType', 'Wrong diagram dictionary wrapper')
                key, value = text(entry, 'a:Key'), entry.find('a:Value', N)
                if value is None:
                    continue
                guid(key, 'Diagram key')
                all_guids.append(key)
                generic, type_id = text(value, 'd:GenericTypeId'), text(value, 'd:TypeId')
                check(text(value, 'd:Guid') == key, 'Diagram key/Guid mismatch: ' + key)
                check(type_id in elements, 'Unknown stencil/flow TypeId: ' + type_id)
                check(generic in ancestry(type_id), 'TypeId/GenericTypeId mismatch: ' + type_id)
                if generic == 'GE.TB.L':
                    check(False, 'Line boundary serialization is unsupported without a populated Core export')
                check(resolved_types.get(id(value)) == (M, SHAPES.get(generic)),
                      'Shape representation mismatch: ' + type_id)
                if generic == 'GE.DF':
                    check(group == 'Lines', 'Line representation must be in Lines')
                else:
                    check(group == 'Borders', 'Border representation must be in Borders')
                if generic == 'GE.DF':
                    members(value, FLOW_MEMBERS, D, 'Connector')
                    for coordinate in ('HandleX', 'HandleY', 'SourceX', 'SourceY', 'TargetX', 'TargetY'):
                        check(re.fullmatch(r'[+-]?[0-9]+', text(value, 'd:' + coordinate)) is not None,
                              'Connector coordinate must be an integer: ' + coordinate)
                    flows[key] = (sid, value)
                elif generic != 'GE.TB.L':
                    members(value, BORDER_MEMBERS, D, 'Border')
                    local_objects[key] = value
                diagram_properties(value, type_id)
        objects[sid] = local_objects
    check(len(surfaces) > 0, 'Model has no drawing surfaces')
    check(len(all_guids) == len(set(all_guids)), 'Duplicate model UUIDs')
    for key, (sid, flow) in flows.items():
        for name in ('SourceGuid', 'TargetGuid'):
            endpoint = text(flow, 'd:' + name)
            check(endpoint in objects[sid], 'Unresolved connector ' + name + ': ' + key)
            if endpoint in objects[sid]:
                check(text(objects[sid][endpoint], 'd:GenericTypeId') in ('GE.P', 'GE.EI', 'GE.DS'),
                      'Connector endpoint must be a process, external interactor, or data store')
    instance_ids, instance_keys = [], []
    entries = root.find('m:ThreatInstances', N)
    for entry in entries if entries is not None else []:
        check(entry.tag == '{' + A + '}KeyValueOfstringThreatpc_P0_PhOB', 'Wrong threat dictionary wrapper')
        members(entry, ['Key', 'Value'], A, 'Threat dictionary entry')
        value = entry.find('a:Value', N)
        if value is None:
            continue
        members(value, THREAT_MEMBERS, K, 'Threat')
        tid, sid = text(value, 'k:TypeId'), text(value, 'k:DrawingSurfaceGuid')
        source, flow, target = [text(value, 'k:' + name) for name in ('SourceGuid', 'FlowGuid', 'TargetGuid')]
        check(tid in threats, 'Unknown Core threat TypeId: ' + tid)
        check(sid in surfaces, 'Unresolved threat DrawingSurfaceGuid')
        check(source in objects.get(sid, {}) and target in objects.get(sid, {}), 'Unresolved threat endpoints')
        check(flow in flows and flows[flow][0] == sid, 'Unresolved threat FlowGuid on drawing surface')
        if flow in flows:
            f = flows[flow][1]
            check((source, target) == (text(f, 'd:SourceGuid'), text(f, 'd:TargetGuid')),
                  'Threat direction disagrees with connector')
        key = text(entry, 'a:Key')
        instance_keys.append(key)
        check(key == tid + source + flow + target, 'Threat dictionary key mismatch: ' + key)
        check(text(value, 'k:InteractionKey') == ':'.join((source, flow, target)), 'Threat InteractionKey mismatch')
        instance_id = text(value, 'k:Id')
        instance_ids.append(instance_id)
        check(instance_id.isdigit() and int(instance_id) > 0, 'Threat Id must be a positive integer')
        props, keys = {}, []
        for prop in value.findall('k:Properties/a:KeyValueOfstringstring', N):
            members(prop, ['Key', 'Value'], A, 'Threat property')
            name = text(prop, 'a:Key')
            keys.append(name)
            props[name] = text(prop, 'a:Value')
        check(len(keys) == len(set(keys)), 'Duplicate threat property keys')
        allowed = property_names | {text(x, 'm:Name') for x in threats.get(tid, ET.Element('empty')).findall(
            'k:PropertiesMetaData/m:ThreatMetaDatum', N)}
        check(set(props).issubset(allowed), 'Unknown Core threat properties: ' + ', '.join(sorted(set(props) - allowed)))
        required = {'Title', 'UserThreatCategory', 'UserThreatShortDescription', 'UserThreatDescription',
                    'InteractionString', 'Priority'}
        check(required.issubset(props) and all(props.get(x) for x in required), 'Missing/empty Core threat properties')
        check(props.get('Priority') == text(value, 'k:Priority') and props.get('Priority') in ('High', 'Medium', 'Low'),
              'Threat priority mismatch')
        if tid in threats:
            category = categories.get(text(threats[tid], 'k:Category'))
            check(category is not None and props.get('UserThreatCategory') == text(category, 'k:Name'),
                  'Threat category disagrees with Core type')
            check(category is not None and props.get('UserThreatShortDescription') == text(category, 'k:ShortDescription'),
                  'Threat short description disagrees with Core category')
    check(len(instance_ids) == len(set(instance_ids)), 'Duplicate numeric threat Ids')
    check(len(instance_keys) == len(set(instance_keys)), 'Duplicate threat dictionary keys')
    counts = {'surfaces': len(surfaces), 'borders': sum(len(x) for x in objects.values()),
              'connectors': len(flows), 'threats': len(instance_ids),
              'core_version': text(manifest, 'k:Version') if manifest is not None else ''}
    return errors, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('models', nargs='+', type=Path)
    parser.add_argument('--template', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'assets/example-minimal.tm7')
    args = parser.parse_args()
    failed = False
    for path in args.models:
        try:
            errors, counts = validate(path, args.template)
        except (ET.ParseError, OSError, ValueError, KeyError, TypeError) as exc:
            errors, counts = [str(exc)], {}
        if errors:
            failed = True
            print('FAIL', path)
            for message in errors:
                print(' -', message)
        else:
            print('PASS', path, counts)
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
