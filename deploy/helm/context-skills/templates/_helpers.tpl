{{- define "context-skills.name" -}}
context-skills
{{- end -}}

{{- define "context-skills.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "context-skills.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "context-skills.labels" -}}
app.kubernetes.io/name: {{ include "context-skills.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "context-skills.selectorLabels" -}}
app.kubernetes.io/name: {{ include "context-skills.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
component: api
{{- end -}}

{{- define "context-skills.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "context-skills.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
