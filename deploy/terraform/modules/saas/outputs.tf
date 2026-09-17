output "api_endpoint" {
  value = module.context_skills.api_endpoint
}

output "console_url" {
  value = module.context_skills.console_url
}

output "opa_endpoint" {
  value = module.context_skills.opa_endpoint
}

output "database_url" {
  value     = module.context_skills.database_url
  sensitive = true
}

output "tenant_namespaces" {
  value = local.tenant_namespace_map
}

output "deployment_mode" {
  value = "saas"
}

output "region" {
  value = var.region
}
