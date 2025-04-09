resource "aws_db_instance" "read_replica" {
  count = var.number_of_replicas

  identifier           = "${var.db_identifier}-replica-${count.index + 1}"
  replicate_source_db = var.source_db_identifier
  instance_class      = var.instance_class
  allocated_storage   = var.allocated_storage
  storage_type        = var.storage_type
  engine              = var.engine
  engine_version      = var.engine_version
  skip_final_snapshot = true

  vpc_security_group_ids = var.vpc_security_group_ids
  db_subnet_group_name   = var.db_subnet_group_name

  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.db_identifier}-replica-${count.index + 1}"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "replica_cpu" {
  count = var.number_of_replicas

  alarm_name          = "${var.db_identifier}-replica-${count.index + 1}-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = var.cpu_utilization_threshold
  alarm_description  = "This metric monitors RDS replica CPU utilization"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.read_replica[count.index].identifier
  }

  alarm_actions = var.alarm_actions
}

resource "aws_cloudwatch_metric_alarm" "replica_memory" {
  count = var.number_of_replicas

  alarm_name          = "${var.db_identifier}-replica-${count.index + 1}-freeable-memory"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = var.memory_threshold
  alarm_description  = "This metric monitors RDS replica freeable memory"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.read_replica[count.index].identifier
  }

  alarm_actions = var.alarm_actions
} 