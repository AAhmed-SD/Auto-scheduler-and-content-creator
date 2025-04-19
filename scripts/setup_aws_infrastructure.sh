#!/bin/bash

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$AWS_REGION" ] || [ -z "$DOMAIN_NAME" ]; then
    echo "Please set AWS_REGION and DOMAIN_NAME environment variables"
    exit 1
fi

# Create VPC
echo "Creating VPC..."
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=auto-scheduler-vpc

# Create Internet Gateway
echo "Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Create Subnets
echo "Creating Subnets..."
SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a --query 'Subnet.SubnetId' --output text)

# Create Route Table
echo "Creating Route Table..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $ROUTE_TABLE_ID --subnet-id $SUBNET_ID

# Create Security Group
echo "Creating Security Group..."
SG_ID=$(aws ec2 create-security-group --group-name auto-scheduler-sg --description "Security group for Auto Scheduler" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0

# Create ECR Repository
echo "Creating ECR Repository..."
aws ecr create-repository --repository-name auto-scheduler --image-scanning-configuration scanOnPush=true

# Create Secrets in Secrets Manager
echo "Creating Secrets in Secrets Manager..."
aws secretsmanager create-secret --name supabase-url --description "Supabase URL"
aws secretsmanager create-secret --name supabase-key --description "Supabase API Key"
aws secretsmanager create-secret --name openai-api-key --description "OpenAI API Key"
aws secretsmanager create-secret --name clip-api-key --description "CLIP API Key"

# Create Route 53 Hosted Zone
echo "Creating Route 53 Hosted Zone..."
HOSTED_ZONE_ID=$(aws route53 create-hosted-zone --name $DOMAIN_NAME --caller-reference $(date +%s) --query 'HostedZone.Id' --output text)

# Request SSL Certificate
echo "Requesting SSL Certificate..."
CERTIFICATE_ARN=$(aws acm request-certificate --domain-name $DOMAIN_NAME --validation-method DNS --query 'CertificateArn' --output text)

# Create ECS Cluster
echo "Creating ECS Cluster..."
aws ecs create-cluster --cluster-name auto-scheduler-cluster

# Create ECS Task Definition
echo "Creating ECS Task Definition..."
cat > task-definition.json << EOF
{
    "family": "auto-scheduler-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "auto-scheduler",
            "image": "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com/auto-scheduler:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "SUPABASE_URL",
                    "value": "{{resolve:secretsmanager:supabase-url}}"
                },
                {
                    "name": "SUPABASE_KEY",
                    "value": "{{resolve:secretsmanager:supabase-key}}"
                },
                {
                    "name": "OPENAI_API_KEY",
                    "value": "{{resolve:secretsmanager:openai-api-key}}"
                },
                {
                    "name": "CLIP_API_KEY",
                    "value": "{{resolve:secretsmanager:clip-api-key}}"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/auto-scheduler",
                    "awslogs-region": "${AWS_REGION}",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create CloudWatch Log Group
echo "Creating CloudWatch Log Group..."
aws logs create-log-group --log-group-name /ecs/auto-scheduler

echo "AWS Infrastructure setup completed!"
echo "Please note the following important information:"
echo "VPC ID: $VPC_ID"
echo "Hosted Zone ID: $HOSTED_ZONE_ID"
echo "Certificate ARN: $CERTIFICATE_ARN"
echo "Security Group ID: $SG_ID"
echo "Subnet ID: $SUBNET_ID" 