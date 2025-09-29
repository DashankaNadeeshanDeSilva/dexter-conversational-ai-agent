#!/bin/bash

# Build and Push Docker Image to ECR for Dexter AI Agent
# This script builds the Lambda container image and pushes it to ECR

set -e  # Exit on any error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
REPO_NAME="${REPO_NAME:-dexter-ai-agent}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME"

echo "🚀 Building and pushing Dexter AI Agent to ECR"
echo "Repository: $REPO_NAME"
echo "Region: $AWS_REGION"
echo "Tag: $IMAGE_TAG"
echo "ECR URI: $ECR_URI"

# Ensure we're in the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Working directory: $PROJECT_ROOT"

# Check if Dockerfile.lambda exists
if [ ! -f "Dockerfile.lambda" ]; then
    echo "❌ Error: Dockerfile.lambda not found in project root"
    exit 1
fi

# Authenticate Docker to ECR
echo "🔐 Authenticating Docker to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$ECR_URI"

# Build the Docker image
echo "🔨 Building Docker image..."
docker buildx build \
    --platform linux/amd64 \
    -f Dockerfile.lambda \
    -t "$REPO_NAME:$IMAGE_TAG" \
    -t "$ECR_URI:$IMAGE_TAG" \
    . \
    --load

echo "✅ Docker image built successfully!"

# Push the image to ECR
echo "📤 Pushing image to ECR..."
docker push "$ECR_URI:$IMAGE_TAG"

echo "✅ Image pushed to ECR successfully!"

# Display image details
echo ""
echo "📋 Image Details:"
echo "Repository URI: $ECR_URI"
echo "Tag: $IMAGE_TAG"
echo "Full Image URI: $ECR_URI:$IMAGE_TAG"

# Test the image locally (optional)
echo ""
read -p "🧪 Do you want to test the image locally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🏃 Running container locally on port 9000..."
    echo "You can test it with: curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations -d '{}'"
    echo "Press Ctrl+C to stop the container"
    docker run --rm -p 9000:8080 --env-file .env "$REPO_NAME:$IMAGE_TAG"
fi

echo ""
echo "🎉 Build and push complete!"
echo "Next step: Run ./deploy-lambda.sh to deploy to AWS Lambda"
