terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

check "region_pin" {
  assert {
    condition     = var.region != ""
    error_message = "Customer VPC deployments require an explicit region pin."
  }
}

module "context_skills" {
  source = "../context-skills"

  region                = var.region
  name_prefix           = "${var.name_prefix}-${var.customer_id}"
  auth_mode             = var.auth_mode
  deployment_mode       = "customer-vpc"
  vpc_cidr              = var.vpc_cidr
  db_password           = var.db_password
  allowed_ingress_cidrs = var.allowed_ingress_cidrs
  tags = merge(var.tags, {
    deployment  = "customer-vpc"
    customer_id = var.customer_id
    region_pin  = var.region
  })
}
