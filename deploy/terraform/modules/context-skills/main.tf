variable "region" {
  type        = string
  description = "Data residency region pin"
  default     = "us-east-1"
}

variable "auth_mode" {
  type    = string
  default = "enforced"
}

variable "deployment_mode" {
  type    = string
  default = "saas"
}

output "api_endpoint" {
  value = "https://context-skills.${var.region}.example.com"
}

output "console_url" {
  value = "https://context-skills.${var.region}.example.com/console/"
}

output "opa_endpoint" {
  value = "http://opa.context-skills.svc:8181"
}
