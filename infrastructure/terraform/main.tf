terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = "us-east-1"  # Change this to your preferred region
}

# Import the auto-scaling configuration
module "autoscaling" {
  source = "./modules/autoscaling"

  min_capacity        = var.min_capacity
  max_capacity        = var.max_capacity
  cpu_target_value    = var.cpu_target_value
  memory_target_value = var.memory_target_value
  scale_in_cooldown   = var.scale_in_cooldown
  scale_out_cooldown  = var.scale_out_cooldown
  rds_max_storage     = var.rds_max_storage
  redis_node_groups   = var.redis_node_groups
  redis_replicas      = var.redis_replicas
  db_password         = var.db_password
}

# Output the auto-scaling configuration details
output "ecs_service_name" {
  value = module.autoscaling.ecs_service_name
}

output "rds_instance_id" {
  value = module.autoscaling.rds_instance_id
}

output "redis_replication_group_id" {
  value = module.autoscaling.redis_replication_group_id
} 