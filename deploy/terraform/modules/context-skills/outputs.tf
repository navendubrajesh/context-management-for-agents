output "api_endpoint" {
  value       = "https://${aws_lb.api.dns_name}"
  description = "REST API URL via ALB"
}

output "console_url" {
  value       = "https://${aws_lb.api.dns_name}/console/"
  description = "Control plane console URL"
}

output "opa_endpoint" {
  value       = "http://context-skills-opa.${var.name_prefix}.svc:8181"
  description = "OPA policy engine cluster URL"
}

output "database_url" {
  value       = "postgresql+psycopg2://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/contextskills"
  description = "Postgres connection string for control plane"
  sensitive   = true
}

output "eks_cluster_name" {
  value = aws_eks_cluster.main.name
}

output "region" {
  value = var.region
}

output "deployment_mode" {
  value = var.deployment_mode
}
