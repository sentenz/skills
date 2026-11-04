# Core XML examples

These are complete XML fragments, formatted for reading. Serialize the final model without
adding indentation. Namespace declarations here make each fragment independently parseable;
declarations already inherited in the final document can retain their exported scope.

[core-worked-example.tm7](./core-worked-example.tm7) is a connected example derived from
the user's blank Core 4.1.0.11 skeleton and populated Core reference blocks: Client (external
interactor) -> Service (process), one generic directional flow, and one S3 spoofing threat.
Its knowledge base is copied unchanged from `assets/example-minimal.tm7`. This is a static
consistency example; Microsoft Threat Modeling Tool open/save validation is separate.

The fragments below use matching UUIDs and serializer IDs. The blank export reserves `i1`
and `i2`; these fragments allocate `i3`, `i4`, and `i5`. The worked model includes all three
diagram fragments and the threat below. Copy full property blocks when adapting them.

## External interactor

```xml
<a:KeyValueOfguidanyType xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/">
<a:Key>148ade68-5c80-40f3-8e1f-4e2cabdb5991</a:Key>
<a:Value z:Id="i3" i:type="StencilRectangle">
<GenericTypeId xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">GE.EI</GenericTypeId>
<Guid xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">148ade68-5c80-40f3-8e1f-4e2cabdb5991</Guid>
<Properties xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">
<a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Generic External Interactor</b:DisplayName>
<b:Name/>
<b:Value i:nil="true"/>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Name</b:DisplayName>
<b:Name/>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema">Client</b:Value>
</a:anyType>
<a:anyType i:type="b:BooleanDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Out Of Scope</b:DisplayName>
<b:Name>71f3d9aa-b8ef-4e54-8126-607a1d903103</b:Name>
<b:Value i:type="c:boolean" xmlns:c="http://www.w3.org/2001/XMLSchema">false</b:Value>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Reason For Out Of Scope</b:DisplayName>
<b:Name>752473b6-52d4-4776-9a24-202153f7d579</b:Name>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema"/>
</a:anyType>
<a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Configurable Attributes</b:DisplayName>
<b:Name/>
<b:Value i:nil="true"/>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Authenticates Itself</b:DisplayName>
<b:Name>authenticatesItself</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Applicable</a:string>
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>1</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Type</b:DisplayName>
<b:Name>type</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Code</a:string>
<a:string>Human</a:string>
</b:Value>
<b:SelectedIndex>1</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Microsoft</b:DisplayName>
<b:Name>MS</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
</Properties>
<TypeId xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">GE.EI</TypeId>
<Height xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Height>
<Left xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Left>
<StrokeDashArray i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts"/>
<StrokeThickness xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">0</StrokeThickness>
<Top xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Top>
<Width xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Width>
</a:Value>
</a:KeyValueOfguidanyType>
```

## Process

```xml
<a:KeyValueOfguidanyType xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/">
<a:Key>cc4f292c-59f9-414c-9af4-2c631ad900de</a:Key>
<a:Value z:Id="i4" i:type="StencilEllipse">
<GenericTypeId xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">GE.P</GenericTypeId>
<Guid xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">cc4f292c-59f9-414c-9af4-2c631ad900de</Guid>
<Properties xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">
<a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Generic Process</b:DisplayName>
<b:Name/>
<b:Value i:nil="true"/>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Name</b:DisplayName>
<b:Name/>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema">Service</b:Value>
</a:anyType>
<a:anyType i:type="b:BooleanDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Out Of Scope</b:DisplayName>
<b:Name>71f3d9aa-b8ef-4e54-8126-607a1d903103</b:Name>
<b:Value i:type="c:boolean" xmlns:c="http://www.w3.org/2001/XMLSchema">false</b:Value>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Reason For Out Of Scope</b:DisplayName>
<b:Name>752473b6-52d4-4776-9a24-202153f7d579</b:Name>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema"/>
</a:anyType>
<a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Configurable Attributes</b:DisplayName>
<b:Name/>
<b:Value i:nil="true"/>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Code Type</b:DisplayName>
<b:Name>codeType</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Managed</a:string>
<a:string>Unmanaged</a:string>
</b:Value>
<b:SelectedIndex>2</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Running As</b:DisplayName>
<b:Name>runningAs</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Kernel</a:string>
<a:string>System</a:string>
<a:string>Network Service</a:string>
<a:string>Local Service</a:string>
<a:string>Administrator</a:string>
<a:string>Standard User With Elevation</a:string>
<a:string>Standard User Without Elevation</a:string>
<a:string>Windows Store App</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Isolation Level</b:DisplayName>
<b:Name>Isolation</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>AppContainer</a:string>
<a:string>Low Integrity Level</a:string>
<a:string>Microsoft Office Isolated Conversion Environment (MOICE)</a:string>
<a:string>Sandbox</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Accepts Input From</b:DisplayName>
<b:Name>acceptsInputFrom</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Any Remote User or Entity</a:string>
<a:string>Kernel, System, or Local Admin</a:string>
<a:string>Local or Network Service</a:string>
<a:string>Local Standard User With Elevation</a:string>
<a:string>Local Standard User Without Elevation</a:string>
<a:string>Windows Store Apps or App Container Processes</a:string>
<a:string>Nothing</a:string>
<a:string>Other</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Implements or Uses an Authentication Mechanism</b:DisplayName>
<b:Name>implementsAuthenticationScheme</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Implements or Uses an Authorization Mechanism</b:DisplayName>
<b:Name>implementsCustomAuthorizationMechanism</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Implements or Uses a Communication Protocol</b:DisplayName>
<b:Name>implementsCommunicationProtocol</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Sanitizes Input</b:DisplayName>
<b:Name>hasInputSanitizers</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Yes</a:string>
<a:string>No</a:string>
</b:Value>
<b:SelectedIndex>1</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Sanitizes Output</b:DisplayName>
<b:Name>hasOutputSanitizers</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Yes</a:string>
<a:string>No</a:string>
</b:Value>
<b:SelectedIndex>1</b:SelectedIndex>
</a:anyType>
</Properties>
<TypeId xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">GE.P</TypeId>
<Height xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Height>
<Left xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">900</Left>
<StrokeDashArray i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts"/>
<StrokeThickness xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">0</StrokeThickness>
<Top xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Top>
<Width xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">100</Width>
</a:Value>
</a:KeyValueOfguidanyType>
```

## Connector

```xml
<a:KeyValueOfguidanyType xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/">
<a:Key>6cae5818-d775-4935-96a4-b317b1fcdecb</a:Key>
<a:Value z:Id="i5" i:type="Connector">
<GenericTypeId xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">GE.DF</GenericTypeId>
<Guid xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">6cae5818-d775-4935-96a4-b317b1fcdecb</Guid>
<Properties xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">
<a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Generic Data Flow</b:DisplayName>
<b:Name/>
<b:Value i:nil="true"/>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Name</b:DisplayName>
<b:Name/>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema">Client to Service via generic data flow (protocol unspecified, protection unknown)</b:Value>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Dataflow Order</b:DisplayName>
<b:Name>15ccd509-98eb-49ad-b9c2-b4a2926d1780</b:Name>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema">0</b:Value>
</a:anyType>
<a:anyType i:type="b:BooleanDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Out Of Scope</b:DisplayName>
<b:Name>71f3d9aa-b8ef-4e54-8126-607a1d903103</b:Name>
<b:Value i:type="c:boolean" xmlns:c="http://www.w3.org/2001/XMLSchema">false</b:Value>
</a:anyType>
<a:anyType i:type="b:StringDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Reason For Out Of Scope</b:DisplayName>
<b:Name>752473b6-52d4-4776-9a24-202153f7d579</b:Name>
<b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema"/>
</a:anyType>
<a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Configurable Attributes</b:DisplayName>
<b:Name/>
<b:Value i:nil="true"/>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Physical Network</b:DisplayName>
<b:Name>channel</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Wire</a:string>
<a:string>Wi-Fi</a:string>
<a:string>Bluetooth</a:string>
<a:string>2G-4G</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Source Authenticated</b:DisplayName>
<b:Name>authenticatesSource</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>1</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Destination Authenticated</b:DisplayName>
<b:Name>authenticatesDestination</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Provides Confidentiality</b:DisplayName>
<b:Name>providesConfidentiality</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Provides Integrity</b:DisplayName>
<b:Name>providesIntegrity</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Transmits XML</b:DisplayName>
<b:Name>XMLenc</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Contains Cookies</b:DisplayName>
<b:Name>Cookies</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Yes</a:string>
<a:string>No</a:string>
</b:Value>
<b:SelectedIndex>1</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>SOAP Payload</b:DisplayName>
<b:Name>SOAP</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>REST Payload</b:DisplayName>
<b:Name>REST</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>RSS Payload</b:DisplayName>
<b:Name>RSS</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>JSON Payload</b:DisplayName>
<b:Name>JSON</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>No</a:string>
<a:string>Yes</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:DisplayName>Forgery Protection</b:DisplayName>
<b:Name>54851a3b-65da-4902-b4e0-94ef015be735</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>ValidateAntiForgeryTokenAttribute</a:string>
<a:string>ViewStateUserKey</a:string>
<a:string>Nonce</a:string>
<a:string>Other dynamic canary</a:string>
<a:string>Static header not available to the browser</a:string>
<a:string>Other</a:string>
<a:string>None</a:string>
<a:string>Not applicable because the request does not change data</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
</Properties>
<TypeId xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">GE.DF</TypeId>
<HandleX xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">550</HandleX>
<HandleY xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">150</HandleY>
<PortSource xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">East</PortSource>
<PortTarget xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">West</PortTarget>
<SourceGuid xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">148ade68-5c80-40f3-8e1f-4e2cabdb5991</SourceGuid>
<SourceX xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">200</SourceX>
<SourceY xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">150</SourceY>
<TargetGuid xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">cc4f292c-59f9-414c-9af4-2c631ad900de</TargetGuid>
<TargetX xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">900</TargetX>
<TargetY xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts">150</TargetY>
</a:Value>
</a:KeyValueOfguidanyType>
```

## List property (from the connector)

```xml
<a:anyType i:type="b:ListDisplayAttribute" xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase" xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/">
<b:DisplayName>Physical Network</b:DisplayName>
<b:Name>channel</b:Name>
<b:Value i:type="a:ArrayOfstring">
<a:string>Not Selected</a:string>
<a:string>Wire</a:string>
<a:string>Wi-Fi</a:string>
<a:string>Bluetooth</a:string>
<a:string>2G-4G</a:string>
</b:Value>
<b:SelectedIndex>0</b:SelectedIndex>
</a:anyType>
```

## Core threat instance

```xml
<a:KeyValueOfstringThreatpc_P0_PhOB xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/">
<a:Key>S3148ade68-5c80-40f3-8e1f-4e2cabdb59916cae5818-d775-4935-96a4-b317b1fcdecbcc4f292c-59f9-414c-9af4-2c631ad900de</a:Key>
<a:Value xmlns:b="http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase">
<b:ChangedBy i:nil="true"/>
<b:DrawingSurfaceGuid>57aa5683-9d8f-4c90-ba1a-0e2ee8d56c2d</b:DrawingSurfaceGuid>
<b:FlowGuid>6cae5818-d775-4935-96a4-b317b1fcdecb</b:FlowGuid>
<b:Id>1</b:Id>
<b:InteractionKey>148ade68-5c80-40f3-8e1f-4e2cabdb5991:6cae5818-d775-4935-96a4-b317b1fcdecb:cc4f292c-59f9-414c-9af4-2c631ad900de</b:InteractionKey>
<b:InteractionString i:nil="true"/>
<b:ModifiedAt>0001-01-01T00:00:00</b:ModifiedAt>
<b:Priority>High</b:Priority>
<b:Properties>
<a:KeyValueOfstringstring>
<a:Key>Title</a:Key>
<a:Value>Spoofing the Client External Entity</a:Value>
</a:KeyValueOfstringstring>
<a:KeyValueOfstringstring>
<a:Key>UserThreatCategory</a:Key>
<a:Value>Spoofing</a:Value>
</a:KeyValueOfstringstring>
<a:KeyValueOfstringstring>
<a:Key>UserThreatShortDescription</a:Key>
<a:Value>Spoofing is when a process or entity is something other than its claimed identity. Examples include substituting a process, a file, website or a network address.</a:Value>
</a:KeyValueOfstringstring>
<a:KeyValueOfstringstring>
<a:Key>UserThreatDescription</a:Key>
<a:Value>Client may be spoofed by an attacker and this may lead to unauthorized access to Service. Consider using a standard authentication mechanism to identify the external entity.</a:Value>
</a:KeyValueOfstringstring>
<a:KeyValueOfstringstring>
<a:Key>InteractionString</a:Key>
<a:Value>Client to Service via generic data flow (protocol unspecified, protection unknown)</a:Value>
</a:KeyValueOfstringstring>
<a:KeyValueOfstringstring>
<a:Key>Priority</a:Key>
<a:Value>High</a:Value>
</a:KeyValueOfstringstring>
</b:Properties>
<b:SourceGuid>148ade68-5c80-40f3-8e1f-4e2cabdb5991</b:SourceGuid>
<b:State>AutoGenerated</b:State>
<b:StateInformation i:nil="true"/>
<b:TargetGuid>cc4f292c-59f9-414c-9af4-2c631ad900de</b:TargetGuid>
<b:Title i:nil="true"/>
<b:TypeId>S3</b:TypeId>
<b:Upgraded>false</b:Upgraded>
<b:UserThreatCategory i:nil="true"/>
<b:UserThreatDescription i:nil="true"/>
<b:UserThreatShortDescription i:nil="true"/>
<b:Wide>false</b:Wide>
</a:Value>
</a:KeyValueOfstringThreatpc_P0_PhOB>
```

