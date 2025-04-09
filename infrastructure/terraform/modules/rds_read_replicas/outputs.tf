output "read_replica_endpoints" {
  description = "The endpoints of the RDS read replicas"
  value       = aws_db_instance.read_replica[*].endpoint
}

output "read_replica_arns" {
  description = "The ARNs of the RDS read replicas"
  value       = aws_db_instance.read_replica[*].arn
} 