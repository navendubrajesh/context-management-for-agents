# Context Skills — Helm chart

Deploy API, MCP, console, OPA sidecar, and OTEL collector.

## Install

```bash
helm install context-skills ./deploy/helm/context-skills \
  --set auth.mode=enforced \
  --set ingress.host=skills.example.com
```

## Values

| Key | Default | Description |
|-----|---------|-------------|
| `auth.mode` | `disabled` | `disabled` or `enforced` |
| `replicaCount` | `2` | API replicas (HA) |
| `autoscaling.enabled` | `true` | HPA |
| `region` | `us-east-1` | Data residency pin |

See `values.yaml` for probes, resources, and TLS defaults.
