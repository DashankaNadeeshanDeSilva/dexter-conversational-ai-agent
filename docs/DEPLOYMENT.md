# Deployment Guide  **==REWRITE/UPDATE ACCORDING TO AWS LAMBDA SERVERLESS DEPLOYMENT==**

**Note that this documentation is created with partial help of GenAI tools.**

This comprehensive guide covers deploying Dexter in production environments, from local containerization to cloud-scale AWS deployments with monitoring and observability.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Production Setup](#local-production-setup)
- [AWS Cloud Deployment](#aws-cloud-deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Configuration Management](#configuration-management)
- [Scaling & Performance](#scaling--performance)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Overview

Dexter supports multiple deployment strategies:

- **Local Production**: Docker Compose for single-server deployments
- **AWS ECS Fargate**: Scalable, serverless container orchestration
- **Hybrid Monitoring**: Prometheus + Grafana observability stack

### Architecture Summary

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   Dexter API     │────│   Memory Layer  │
│   (ALB/Nginx)   │    │   (FastAPI)      │    │   (MongoDB +    │
└─────────────────┘    └──────────────────┘    │   Pinecone)     │
                                               └─────────────────┘
                              │
                    ┌─────────────────┐
                    │   Monitoring    │
                    │   (Prometheus + │
                    │   Grafana)      │
                    └─────────────────┘
```

## Prerequisites

### Required Services

- **MongoDB**: 5.0+ (Atlas recommended for production)
- **Pinecone**: Vector database account and API key
- **OpenAI**: API key for LLM services
- **LangChain**: API key for tracing (optional but recommended)

### Infrastructure Requirements

- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB storage
- **Network**: HTTPS/TLS termination capability

### Development Tools

- **Docker**: 20.10+ with Docker Compose
- **AWS CLI**: 2.0+ (for cloud deployment)
- **Git**: Version control access

## Local Production Setup

### Docker Compose Deployment

Perfect for single-server production deployments or staging environments.

#### 1. Environment Configuration

Create production environment file:

```bash
# Create production environment
cp .env.example .env.production

# Edit with production values
nano .env.production
```

**Required Environment Variables**:

```env
# Production Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/dexter_production
# For external MongoDB:
# MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/dexter

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# AI Services
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING=true
LANGCHAIN_PROJECT=dexter-production

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=["your-domain.com", "localhost"]
```

#### 2. SSL/TLS Configuration (Recommended)

For production HTTPS, extend `docker-compose.yml`:

```yaml
# Add to docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

  app:
    # Remove direct port exposure
    # ports:
    #   - "8000:8000"
    expose:
      - "8000"
```

#### 3. Deploy Application

```bash
# Start production services
docker-compose --env-file .env.production up -d

# Verify deployment
docker-compose ps
docker-compose logs app

# Check health endpoint
curl http://localhost:8000/health
```

#### 4. Database Initialization

```bash
# Run database migrations (if applicable)
docker-compose exec app python scripts/init_database.py

# Verify connectivity
docker-compose exec app python -c "
from app.memory.mongodb_client import MongoDBClient
client = MongoDBClient()
print('MongoDB connection: OK')
"
```

## AWS Cloud Deployment

### ECS Fargate Deployment

Production-ready, scalable deployment using AWS managed services.

#### 1. Pre-deployment Setup

**Install AWS CLI and configure credentials**:

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify access
aws sts get-caller-identity
```

**Set up external services**:

```bash
# MongoDB Atlas (recommended)
# 1. Create cluster at https://cloud.mongodb.com
# 2. Configure network access for AWS region
# 3. Get connection string

# Pinecone setup
# 1. Create index at https://app.pinecone.io
# 2. Note environment and API key
```

#### 2. Container Registry Setup

```bash
# Create ECR repository
aws ecr create-repository --repository-name dexter-ai-agent

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t dexter-ai-agent .
docker tag dexter-ai-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dexter-ai-agent:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dexter-ai-agent:latest
```

#### 3. CloudFormation Deployment

```bash
# Deploy infrastructure
aws cloudformation create-stack \
  --stack-name dexter-production \
  --template-body file://deployment/aws/cloudformation.yml \
  --parameters \
    ParameterKey=Environment,ParameterValue=Production \
    ParameterKey=ContainerImage,ParameterValue=<account-id>.dkr.ecr.us-east-1.amazonaws.com/dexter-ai-agent:latest \
    ParameterKey=MongoDBUri,ParameterValue="mongodb+srv://user:pass@cluster.mongodb.net/dexter" \
    ParameterKey=PineconeApiKey,ParameterValue="your-pinecone-key" \
    ParameterKey=PineconeEnvironment,ParameterValue="your-pinecone-env" \
    ParameterKey=OpenAIApiKey,ParameterValue="your-openai-key" \
    ParameterKey=LangChainApiKey,ParameterValue="your-langchain-key" \
  --capabilities CAPABILITY_IAM

# Monitor deployment
aws cloudformation wait stack-create-complete --stack-name dexter-production

# Get deployment outputs
aws cloudformation describe-stacks --stack-name dexter-production --query 'Stacks[0].Outputs'
```

#### 4. Verify Deployment

```bash
# Get load balancer DNS
ALB_DNS=$(aws cloudformation describe-stacks \
  --stack-name dexter-production \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text)

# Test health endpoint
curl http://$ALB_DNS/health

# Test API functionality
curl -X POST http://$ALB_DNS/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "session_id": "test-session"}'
```

### Blue-Green Deployment

For zero-downtime updates:

```bash
# Update task definition with new image
aws ecs register-task-definition \
  --family production-dexter-ai-agent \
  --container-definitions file://new-task-definition.json

# Update service to use new task definition
aws ecs update-service \
  --cluster dexter-production-cluster \
  --service dexter-production-service \
  --task-definition production-dexter-ai-agent:NEW_REVISION

# Monitor deployment
aws ecs wait services-stable \
  --cluster dexter-production-cluster \
  --services dexter-production-service
```

## Monitoring & Observability

### Prometheus Configuration

The included Prometheus setup automatically scrapes metrics from:

- **Application metrics**: Custom FastAPI metrics on `:8000/metrics`
- **System metrics**: Container resource usage
- **Database metrics**: MongoDB connection pool stats

**Key Metrics to Monitor**:

```yaml
# Application Performance
- http_requests_total
- http_request_duration_seconds
- active_sessions_count
- memory_operations_total

# Resource Utilization  
- cpu_usage_percent
- memory_usage_bytes
- disk_io_operations

# Business Metrics
- chat_messages_processed
- memory_retrievals_count
- tool_executions_total
```

### Grafana Dashboards

Access Grafana at `http://your-domain:3000` (admin/admin)

**Pre-configured Dashboards**:

1. **Application Overview**: Request rates, response times, error rates
2. **Memory System**: MongoDB operations, Pinecone queries, cache hits
3. **Infrastructure**: CPU, memory, network, disk usage
4. **Business Intelligence**: User engagement, feature usage

### Log Management

**Production Logging Configuration**:

```python
# app/utils/logging_utils.py
import structlog

# Structured logging for better observability
logger = structlog.get_logger()

# Log levels by environment
PRODUCTION_LOG_CONFIG = {
    "version": 1,
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/dexter/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    }
}
```

**AWS CloudWatch Integration**:

```bash
# Install CloudWatch agent (for EC2)
sudo yum install amazon-cloudwatch-agent

# Configure log forwarding
aws logs create-log-group --log-group-name /ecs/dexter-production

# Logs automatically forwarded from ECS Fargate
```

### Alerting

**Critical Alerts**:

```yaml
# prometheus-alerts.yml
groups:
  - name: dexter-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseConnectionFailure
        expr: mongodb_connections_failed_total > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MongoDB connection failures"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
```

## Configuration Management

### Environment-Specific Configs

```python
# app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Environment detection
    environment: str = "development"
    debug: bool = False
    
    # Performance tuning by environment
    workers: int = 1 if environment == "development" else 4
    max_connections: int = 10 if environment == "development" else 100
    
    # Security
    secret_key: str
    allowed_hosts: list = ["localhost"]
    
    # Feature flags
    enable_tracing: bool = True
    enable_caching: bool = True
    
    class Config:
        env_file = f".env.{environment}"
```

### Secrets Management

**AWS Secrets Manager Integration**:

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client('secretsmanager', region_name=region_name)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e

# Usage in app/config.py
if environment == "production":
    openai_api_key = get_secret("dexter/openai-api-key")
    mongodb_uri = get_secret("dexter/mongodb-uri")
```

### Feature Flags

```python
# app/config.py
class FeatureFlags:
    ENABLE_ADVANCED_REASONING = True
    ENABLE_TOOL_CACHING = True
    ENABLE_MEMORY_COMPRESSION = False
    MAX_CONVERSATION_LENGTH = 50
    
    @classmethod
    def for_environment(cls, env: str):
        if env == "production":
            cls.ENABLE_MEMORY_COMPRESSION = True
            cls.MAX_CONVERSATION_LENGTH = 100
        return cls
```

## Scaling & Performance

### Horizontal Scaling

**ECS Service Auto Scaling**:

```yaml
# Add to CloudFormation template
AutoScalingTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MaxCapacity: 10
    MinCapacity: 2
    ResourceId: !Sub service/${ECSCluster}/${ECSService}
    RoleARN: !Sub arn:aws:iam::${AWS::AccountId}:role/application-autoscaling-ecs-service
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs

AutoScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: DeXterCPUScalingPolicy
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref AutoScalingTarget
    TargetTrackingScalingPolicyConfiguration:
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageCPUUtilization
      TargetValue: 70.0
```

### Performance Optimization

**Database Optimization**:

```python
# MongoDB connection pooling
mongodb_client = MongoClient(
    uri,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    serverSelectionTimeoutMS=5000
)

# Pinecone optimization
pinecone_config = {
    "batch_size": 100,
    "timeout": 10,
    "retries": 3
}
```

**Caching Strategy**:

```python
# Redis caching for frequent queries
import redis
from functools import lru_cache

redis_client = redis.Redis(host='redis', port=6379, db=0)

@lru_cache(maxsize=1000)
def get_cached_response(query_hash):
    return redis_client.get(f"response:{query_hash}")
```

### Load Testing

```bash
# Install load testing tools
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://your-domain.com

# Monitor during load test
watch -n 2 'docker stats'
```

## Security Considerations

### API Security

```python
# app/utils/auth_utils.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Security(security)):
    # Implement JWT validation
    if not validate_jwt(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
```

### Network Security

**AWS Security Groups**:
- API access only through ALB
- Database access restricted to application subnets
- Monitoring ports internal only

**Docker Security**:

```dockerfile
# Use non-root user
FROM python:3.11-slim
RUN groupadd -r dexter && useradd -r -g dexter dexter
USER dexter

# Security scanning
RUN pip install safety
RUN safety check
```

### Data Protection

```python
# Encrypt sensitive data at rest
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## Troubleshooting

### Common Issues

**1. Memory System Connection Failures**

```bash
# Debug MongoDB connection
docker-compose exec app python -c "
from app.memory.mongodb_client import MongoDBClient
try:
    client = MongoDBClient()
    print('MongoDB: Connected')
except Exception as e:
    print(f'MongoDB Error: {e}')
"

# Debug Pinecone connection
docker-compose exec app python -c "
from app.db_clients.pinecone_client import PineconeClient
try:
    client = PineconeClient()
    print('Pinecone: Connected')
except Exception as e:
    print(f'Pinecone Error: {e}')
"
```

**2. High Memory Usage**

```bash
# Check memory usage
docker stats

# Profile memory usage
docker-compose exec app python -m memory_profiler app/main.py

# Optimize memory settings
export PYTHONHASHSEED=1
export MALLOC_ARENA_MAX=2
```

**3. Performance Issues**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Profile API responses
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/chat

# Check database performance
docker-compose exec mongodb mongo --eval "db.runCommand({serverStatus:1}).connections"
```

### Health Checks

**Application Health Endpoint**:

```python
# app/api/main.py
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database connectivity
    try:
        mongodb_client.admin.command('ping')
        health_status["checks"]["mongodb"] = "healthy"
    except Exception:
        health_status["checks"]["mongodb"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Vector database connectivity
    try:
        pinecone_client.describe_index_stats()
        health_status["checks"]["pinecone"] = "healthy"
    except Exception:
        health_status["checks"]["pinecone"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    return health_status
```

### Monitoring Commands

```bash
# Real-time logs
docker-compose logs -f app

# Resource monitoring
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Database monitoring
docker-compose exec mongodb mongo --eval "db.stats()"

# Check API performance
curl -X GET http://localhost:8000/metrics
```

### Recovery Procedures

**Database Recovery**:

```bash
# Backup before recovery
docker-compose exec mongodb mongodump --out /backup

# Restore from backup
docker-compose exec mongodb mongorestore /backup
```

**Service Recovery**:

```bash
# Restart individual services
docker-compose restart app

# Full environment restart
docker-compose down && docker-compose up -d

# AWS ECS service restart
aws ecs update-service --cluster dexter-cluster --service dexter-service --force-new-deployment
```

---

## Quick Reference

### Essential Commands

```bash
# Local Development
docker-compose up -d                    # Start services
docker-compose logs -f app              # View logs
docker-compose down                     # Stop services

# Production Deployment
aws cloudformation create-stack --template-body file://deployment/aws/cloudformation.yml
aws ecs update-service --force-new-deployment

# Monitoring
curl http://localhost:8000/health       # Health check
curl http://localhost:8000/metrics      # Prometheus metrics
open http://localhost:3000              # Grafana dashboard

# Troubleshooting
docker stats                            # Resource usage
docker-compose exec app python -c "..."  # Debug scripts
aws logs tail /ecs/dexter-production    # AWS logs
```

### Support Contacts

- **Technical Issues**: Create issue on GitHub repository
- **Security Concerns**: Email security@yourcompany.com
- **Performance Issues**: Check monitoring dashboards first
- **Emergency Escalation**: On-call rotation via PagerDuty

For additional support and documentation updates, visit the [GitHub repository](https://github.com/yourusername/dexter-conversational-ai-agent).
