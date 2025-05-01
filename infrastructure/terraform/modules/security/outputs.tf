# Outputs for security module

output "ecs_security_group_id" {
  description = "ID of the ECS tasks security group"
  value       = aws_security_group.ecs_tasks.id
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "secrets_manager_arns" {
  description = "ARNs of Secrets Manager secrets"
  value = {
    supabase = aws_secretsmanager_secret.supabase.arn
    openai   = aws_secretsmanager_secret.openai.arn
    clip     = aws_secretsmanager_secret.clip.arn
  }
}

output "db_subnet_group_name" {
  description = "Name of the database subnet group"
  value       = aws_db_subnet_group.main.name
}

output "monitoring_role_arn" {
  description = "ARN of the IAM role for monitoring"
  value       = aws_iam_role.monitoring.arn
} 