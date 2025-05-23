variable "min_capacity" {
  description = "Minimum number of tasks to run"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks to run"
  type        = number
  default     = 10
}

variable "cpu_target_value" {
  description = "Target CPU utilization percentage for auto-scaling"
  type        = number
  default     = 70
}

variable "memory_target_value" {
  description = "Target memory utilization percentage for auto-scaling"
  type        = number
  default     = 70
}

variable "scale_in_cooldown" {
  description = "Cooldown period in seconds before scaling in"
  type        = number
  default     = 300
}

variable "scale_out_cooldown" {
  description = "Cooldown period in seconds before scaling out"
  type        = number
  default     = 300
}

variable "rds_max_storage" {
  description = "Maximum storage size in GB for RDS instance"
  type        = number
  default     = 100
}

variable "redis_node_groups" {
  description = "Number of node groups in Redis cluster"
  type        = number
  default     = 1
}

variable "redis_replicas" {
  description = "Number of replicas per node group in Redis cluster"
  type        = number
  default     = 1
}

variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
  sensitive   = true
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "number_of_replicas" {
  description = "Number of RDS read replicas to create"
  type        = number
  default     = 2
}

variable "instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
  default     = "db.t3.medium"
}

variable "allocated_storage" {
  description = "The allocated storage in gigabytes"
  type        = number
  default     = 20
}

variable "storage_type" {
  description = "The storage type for the RDS instance"
  type        = string
  default     = "gp2"
}

variable "engine" {
  description = "The database engine to use"
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "The engine version to use"
  type        = string
  default     = "13.7"
}

variable "vpc_security_group_ids" {
  description = "List of VPC security groups to associate"
  type        = list(string)
}

variable "db_subnet_group_name" {
  description = "Name of the DB subnet group"
  type        = string
}

variable "monitoring_interval" {
  description = "The interval, in seconds, between points when Enhanced Monitoring metrics are collected"
  type        = number
  default     = 60
}

variable "monitoring_role_arn" {
  description = "The ARN for the IAM role that permits RDS to send enhanced monitoring metrics to CloudWatch Logs"
  type        = string
}

variable "cpu_utilization_threshold" {
  description = "The threshold for CPU utilization alarm"
  type        = number
  default     = 80
}

variable "memory_threshold" {
  description = "The threshold for freeable memory alarm"
  type        = number
  default     = 1000000000
}

variable "alarm_actions" {
  description = "The list of actions to execute when the alarm transitions into an ALARM state"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Environment name (e.g., development, production)"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "CPU units for the container"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory limit for the container in MiB"
  type        = number
  default     = 512
}

variable "container_image" {
  description = "Docker image for the container"
  type        = string
  default     = "nginx:latest"
}

variable "desired_count" {
  description = "Desired number of containers"
  type        = number
  default     = 1
}

variable "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
} 