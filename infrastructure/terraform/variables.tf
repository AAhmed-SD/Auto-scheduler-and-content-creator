# Auto-scaling variables

variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
  sensitive   = true
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
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
  default     = 80
}

variable "scale_in_cooldown" {
  description = "Cooldown period for scale-in operations in seconds"
  type        = number
  default     = 300
}

variable "scale_out_cooldown" {
  description = "Cooldown period for scale-out operations in seconds"
  type        = number
  default     = 300
}

variable "rds_max_storage" {
  description = "Maximum storage for RDS instance in GB"
  type        = number
  default     = 100
}

variable "redis_node_groups" {
  description = "Number of Redis node groups"
  type        = number
  default     = 2
}

variable "redis_replicas" {
  description = "Number of replicas per Redis node group"
  type        = number
  default     = 1
} 