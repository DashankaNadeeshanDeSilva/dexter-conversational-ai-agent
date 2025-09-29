#!/bin/bash

# Create ECR Repository for Dexter AI Agent
# This script creates an ECR repository if it doesn't exist

set -e  # Exit on any error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
REPO_NAME="${REPO_NAME:-dexter-ai-agent}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Creating ECR repository for Dexter AI Agent"
echo "Region: $AWS_REGION"
echo "Repository: $REPO_NAME"
echo "Account ID: $AWS_ACCOUNT_ID"

# Check if repository already exists
if aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "✅ Repository $REPO_NAME already exists in $AWS_REGION"
else
    echo "📦 Creating ECR repository: $REPO_NAME"
    aws ecr create-repository \
        --repository-name "$REPO_NAME" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    
    echo "✅ ECR repository created successfully!"
fi

# Display repository details
echo ""
echo "📋 Repository Details:"
echo "Repository URI: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME"
echo "Region: $AWS_REGION"

# Set lifecycle policy to manage old images
echo ""
echo "🔧 Setting up lifecycle policy..."
aws ecr put-lifecycle-policy \
    --repository-name "$REPO_NAME" \
    --region "$AWS_REGION" \
    --lifecycle-policy-text '{
        "rules": [
            {
                "rulePriority": 1,
                "description": "Keep last 10 images",
                "selection": {
                    "tagStatus": "any",
                    "countType": "imageCountMoreThan",
                    "countNumber": 10
                },
                "action": {
                    "type": "expire"
                }
            }
        ]
    }'

echo "✅ Lifecycle policy set (keeps last 10 images)"
echo ""
echo "🎉 ECR repository setup complete!"
echo "Next step: Run ./build-and-push.sh to build and push your Docker image"
