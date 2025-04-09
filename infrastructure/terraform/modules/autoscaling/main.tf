# ECS Cluster
resource "aws_ecs_cluster" "auto_scheduler" {
  name = "auto-scheduler-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# ECS Service with Auto-scaling
resource "aws_ecs_service" "auto_scheduler" {
  name            = "auto-scheduler-service"
  cluster         = aws_ecs_cluster.auto_scheduler.id
  task_definition = aws_ecs_task_definition.auto_scheduler.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.auto_scheduler.arn
    container_name   = "auto-scheduler"
    container_port   = 8000
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Auto-scaling Target
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.auto_scheduler.name}/${aws_ecs_service.auto_scheduler.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto-scaling Policies
resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  name               = "cpu-auto-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 300

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

resource "aws_appautoscaling_policy" "ecs_policy_memory" {
  name               = "memory-auto-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 300

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
  }
}

# RDS Instance with Multi-AZ
resource "aws_db_instance" "auto_scheduler" {
  identifier             = "auto-scheduler-db"
  engine                 = "postgres"
  engine_version         = "14.7"
  instance_class         = "db.t3.medium"
  allocated_storage      = 100
  max_allocated_storage  = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  multi_az              = true
  publicly_accessible   = false

  db_name                = "auto_scheduler"
  username               = var.db_username
  password               = var.db_password
  port                   = 5432

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.auto_scheduler.name

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval            = 60
  monitoring_role_arn           = aws_iam_role.rds_monitoring.arn

  performance_insights_enabled = true
  performance_insights_retention_period = 7

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Redis Cluster with Auto-scaling
resource "aws_elasticache_replication_group" "auto_scheduler" {
  replication_group_id       = "auto-scheduler-redis"
  description                = "Redis cluster for Auto Scheduler"
  node_type                  = "cache.t3.medium"
  num_cache_clusters         = 2
  port                       = 6379
  parameter_group_name       = "default.redis6.x"
  automatic_failover_enabled = true
  multi_az_enabled          = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  subnet_group_name  = aws_elasticache_subnet_group.auto_scheduler.name
  security_group_ids = [aws_security_group.redis.id]

  maintenance_window = "Mon:04:00-Mon:05:00"
  snapshot_retention_limit = 7
  snapshot_window         = "03:00-04:00"

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Outputs
output "ecs_service_name" {
  value = aws_ecs_service.auto_scheduler.name
}

output "rds_instance_id" {
  value = aws_db_instance.auto_scheduler.id
}

output "redis_replication_group_id" {
  value = aws_elasticache_replication_group.auto_scheduler.id
}

module "rds_read_replicas" {
  source = "../rds_read_replicas"

  number_of_replicas         = var.number_of_replicas
  db_identifier              = aws_db_instance.auto_scheduler.identifier
  source_db_identifier       = aws_db_instance.auto_scheduler.identifier
  instance_class            = var.instance_class
  allocated_storage         = var.allocated_storage
  storage_type              = var.storage_type
  engine                    = var.engine
  engine_version            = var.engine_version
  vpc_security_group_ids    = var.vpc_security_group_ids
  db_subnet_group_name      = var.db_subnet_group_name
  monitoring_interval       = var.monitoring_interval
  monitoring_role_arn       = var.monitoring_role_arn
  cpu_utilization_threshold = var.cpu_utilization_threshold
  memory_threshold          = var.memory_threshold
  alarm_actions             = var.alarm_actions
  tags                      = var.tags
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu" {
  alarm_name          = "ecs-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period             = "300"
  statistic          = "Average"
  threshold          = 70
  alarm_description  = "This metric monitors ECS CPU utilization"

  dimensions = {
    ClusterName = aws_ecs_cluster.auto_scheduler.name
    ServiceName = aws_ecs_service.auto_scheduler.name
  }

  alarm_actions = var.alarm_actions
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory" {
  alarm_name          = "ecs-memory-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period             = "300"
  statistic          = "Average"
  threshold          = 70
  alarm_description  = "This metric monitors ECS memory utilization"

  dimensions = {
    ClusterName = aws_ecs_cluster.auto_scheduler.name
    ServiceName = aws_ecs_service.auto_scheduler.name
  }

  alarm_actions = var.alarm_actions
} 