# Environment variables
variable "environment" {
  description = "Environment (e.g., development, production)"
  type        = string
  default     = "development"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b"]
}

# Auto-scaling variables
variable "min_capacity" {
  description = "Minimum number of ECS tasks to run for the service"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks to run for the service"
  type        = number
  default     = 10
}

variable "cpu_target_value" {
  description = "Target CPU utilization percentage (0-100) that triggers autoscaling"
  type        = number
  default     = 75
}

variable "memory_target_value" {
  description = "Target memory utilization percentage (0-100) that triggers autoscaling"
  type        = number
  default     = 85
}

variable "scale_in_cooldown" {
  description = "Time in seconds to wait between scale-in operations"
  type        = number
  default     = 300
}

variable "scale_out_cooldown" {
  description = "Time in seconds to wait between scale-out operations"
  type        = number
  default     = 180
}

# Database Configuration
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
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

variable "rds_max_storage" {
  description = "Maximum storage for RDS instance in GB"
  type        = number
  default     = 100
}

# Redis Configuration
variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_node_groups" {
  description = "Number of Redis node groups"
  type        = number
  default     = 1
}

variable "redis_replicas" {
  description = "Number of replicas per Redis node group"
  type        = number
  default     = 0
}

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {
    Environment = "development"
    ManagedBy  = "terraform"
  }
}

# Container Configuration
variable "container_cpu" {
  description = "CPU units for the container (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory for the container in MiB"
  type        = number
  default     = 512
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
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

# Service Discovery
variable "service_discovery_namespace" {
  description = "Name of the service discovery namespace"
  type        = string
  default     = "local"
}

# Health Check
variable "health_check_path" {
  description = "Path for health check"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "Interval between health checks (in seconds)"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Timeout for health check (in seconds)"
  type        = number
  default     = 5
}

variable "health_check_healthy_threshold" {
  description = "Number of consecutive health check successes required"
  type        = number
  default     = 3
}

variable "health_check_unhealthy_threshold" {
  description = "Number of consecutive health check failures required"
  type        = number
  default     = 3
}

# Monitoring and Logging
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# Deployment Configuration
variable "deployment_maximum_percent" {
  description = "Maximum percentage of tasks that can run during deployment"
  type        = number
  default     = 200
}

variable "deployment_minimum_healthy_percent" {
  description = "Minimum percentage of tasks that must remain healthy during deployment"
  type        = number
  default     = 100
}