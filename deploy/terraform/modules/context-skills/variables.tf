variable "region" {
  type        = string
  description = "AWS region pin for data residency"
  default     = "us-east-1"
}

variable "name_prefix" {
  type        = string
  description = "Resource name prefix"
  default     = "context-skills"
}

variable "auth_mode" {
  type    = string
  default = "enforced"
}

variable "deployment_mode" {
  type        = string
  description = "saas or customer-vpc"
  default     = "saas"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_username" {
  type    = string
  default = "contextskills"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "change-me-in-production"
}

variable "eks_version" {
  type    = string
  default = "1.29"
}

variable "allowed_ingress_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "tags" {
  type    = map(string)
  default = { project = "context-skills" }
}
