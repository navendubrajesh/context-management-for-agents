module "context_skills" {
  source = "../context-skills"

  region          = var.region
  name_prefix     = "${var.name_prefix}-saas"
  auth_mode       = var.auth_mode
  deployment_mode = "saas"
  vpc_cidr        = var.vpc_cidr
  db_password     = var.db_password
  tags            = merge(var.tags, { deployment = "saas" })
}

locals {
  tenant_namespace_map = {
    for ns in var.tenant_namespaces : ns => {
      namespace = ns
      shared_opa = true
    }
  }
}
