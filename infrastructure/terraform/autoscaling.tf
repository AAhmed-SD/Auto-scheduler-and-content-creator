# Call the autoscaling module
module "autoscaling" {
  source = "./modules/autoscaling"

  environment = var.environment
  tags        = var.tags

  # VPC and Network
  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  vpc_security_group_ids = [module.security.ecs_security_group_id]
  db_subnet_group_name   = module.security.db_subnet_group_name

  # IAM Roles
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  ecs_task_role_arn          = module.security.ecs_task_execution_role_arn

  # Auto-scaling Configuration
  min_capacity        = var.min_capacity
  max_capacity        = var.max_capacity
  cpu_target_value    = var.cpu_target_value
  memory_target_value = var.memory_target_value
  scale_in_cooldown   = var.scale_in_cooldown
  scale_out_cooldown  = var.scale_out_cooldown

  # Database Configuration
  db_password           = var.db_password
  db_username          = var.db_username
  rds_instance_class   = var.rds_instance_class
  rds_allocated_storage = var.rds_allocated_storage
  rds_max_storage      = var.rds_max_storage
  monitoring_role_arn  = module.security.monitoring_role_arn

  # Redis Configuration
  redis_node_type    = var.redis_node_type
  redis_node_groups  = var.redis_node_groups
  redis_replicas     = var.redis_replicas

  # Container Configuration
  container_cpu    = var.container_cpu
  container_memory = var.container_memory
  container_port   = var.container_port
  container_image  = var.container_image
  desired_count    = var.desired_count
} 