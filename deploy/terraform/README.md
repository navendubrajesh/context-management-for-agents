# Terraform module — context skills stack

Provisions VPC-scoped runtime + control plane for customer-VPC / SaaS modes.

## Usage

```hcl
module "context_skills" {
  source = "./deploy/terraform/modules/context-skills"
  region = "eu-west-1"
  auth_mode = "enforced"
  deployment_mode = "customer-vpc"
}
```

## Outputs

- `api_endpoint` — REST API URL
- `console_url` — control plane console
- `opa_endpoint` — policy engine

## Data residency

Set `region` to pin storage, inference endpoints, and telemetry export.
