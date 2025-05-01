# Variables for security module

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "allowed_ingress_ports" {
  description = "List of allowed ingress ports"
  type        = list(number)
  default     = [8000, 443, 80]
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
} 