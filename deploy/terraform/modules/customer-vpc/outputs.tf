output "api_endpoint" {
  value = module.context_skills.api_endpoint
}

output "console_url" {
  value = module.context_skills.console_url
}

output "database_url" {
  value     = module.context_skills.database_url
  sensitive = true
}

output "deployment_mode" {
  value = "customer-vpc"
}

output "region" {
  value = var.region
}

output "customer_id" {
  value = var.customer_id
}
