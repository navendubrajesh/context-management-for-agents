# Context Skills — Helm chart

Deploy API, OPA policy engine, ingress, HPA, and console configuration.

## Install

```bash
helm lint deploy/helm/context-skills
helm install context-skills ./deploy/helm/context-skills \
  --set auth.mode=enforced \
  --set ingress.host=skills.example.com
```

## Templates

| Template | Resource |
|----------|----------|
| `deployment.yaml` | API Deployment |
| `service.yaml` | ClusterIP Service |
| `ingress.yaml` | Ingress (optional) |
| `hpa.yaml` | HorizontalPodAutoscaler (optional) |
| `configmap.yaml` | Runtime env config |
| `secret.yaml` | OIDC HMAC secret placeholder |
| `opa-deployment.yaml` | OPA Deployment + Service |
| `opa-configmap.yaml` | Bundled Rego policy |
| `serviceaccount.yaml` | ServiceAccount |

## Values

| Key | Default | Description |
|-----|---------|-------------|
| `auth.mode` | `disabled` | `disabled` or `enforced` |
| `replicaCount` | `2` | API replicas (HA) |
| `autoscaling.enabled` | `true` | HPA |
| `region` | `us-east-1` | Data residency pin |
| `opa.enabled` | `true` | Deploy OPA policy engine |
| `console.enabled` | `true` | Enable console via env |
| `ingress.enabled` | `true` | Create Ingress resource |

See `values.yaml` for probes, resources, OTEL, and TLS defaults.
