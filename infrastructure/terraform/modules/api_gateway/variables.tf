variable "redis_replication_group_id" {
  description = "The ID of the Redis replication group"
  type        = string
}

variable "lambda_function_zip" {
  description = "Path to the Lambda function zip file"
  type        = string
} 