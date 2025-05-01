terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}

locals {
  name = "${var.environment}-content-scheduler"
  tags = merge(var.tags, {
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}

provider "aws" {
  region = var.region
}

data "aws_region" "current" {}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "ecs_service_name" {
  value = module.autoscaling.ecs_service_name
}

output "rds_instance_id" {
  value = module.autoscaling.rds_instance_id
}

output "redis_replication_group_id" {
  value = module.autoscaling.redis_replication_group_id
} 