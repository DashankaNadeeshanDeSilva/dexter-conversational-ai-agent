#!/bin/bash

# Complete Deployment Script for Dexter AI Agent
# This script runs all deployment steps in sequence

set -e  # Exit on any error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
REPO_NAME="${REPO_NAME:-dexter-ai-agent}"
FUNCTION_NAME="${FUNCTION_NAME:-dexter-ai-agent}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 Starting complete deployment of Dexter AI Agent"
echo "Region: $AWS_REGION"
echo "Repository: $REPO_NAME"
echo "Function: $FUNCTION_NAME"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Create ECR Repository
echo "📦 Step 1: Creating ECR Repository"
echo "================================"
bash "$SCRIPT_DIR/create-ecr-repo.sh"
echo ""

# Step 2: Build and Push Docker Image
echo "🔨 Step 2: Building and Pushing Docker Image"
echo "============================================="
bash "$SCRIPT_DIR/build-and-push.sh"
echo ""

# Step 3: Deploy Lambda Function
echo "⚡ Step 3: Deploying Lambda Function"
echo "===================================="
bash "$SCRIPT_DIR/deploy-lambda.sh"
echo ""

# Step 4: Setup API Gateway (optional)
echo "🌐 Step 4: Setting up API Gateway"
echo "=================================="
read -p "Do you want to set up API Gateway? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    bash "$SCRIPT_DIR/setup-api-gateway.sh"
else
    echo "⏭️  Skipping API Gateway setup"
fi

echo ""
echo "🎉 Complete deployment finished!"
echo ""
echo "📋 Summary:"
echo "✅ ECR Repository: $REPO_NAME"
echo "✅ Lambda Function: $FUNCTION_NAME"
echo "✅ Region: $AWS_REGION"
echo ""
echo "🔧 Next Steps:"
echo "1. Set up environment variables for your databases (MongoDB, Pinecone, OpenAI)"
echo "2. Test your endpoints"
echo "3. Set up monitoring and logging"
echo ""
echo "📚 Useful Commands:"
echo "• View logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo "• Update function: aws lambda update-function-code --function-name $FUNCTION_NAME --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest"
echo "• Test function: aws lambda invoke --function-name $FUNCTION_NAME response.json"
