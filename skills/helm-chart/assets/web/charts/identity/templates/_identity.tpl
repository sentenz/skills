{{- define "identity.v1.name" -}}
{{- if contains "." .Release.Name -}}
{{- printf "dot-%s-%s" (.Release.Name | replace "." "-" | trunc 43 | trimSuffix "-") (.Release.Name | sha256sum | trunc 10) -}}
{{- else -}}
{{- printf "web-%s" .Release.Name -}}
{{- end -}}
{{- end -}}

{{- define "identity.v1.selector" -}}
app.kubernetes.io/name: web
app.kubernetes.io/instance: {{ .Release.Name | quote }}
app.kubernetes.io/component: server
{{- end -}}
