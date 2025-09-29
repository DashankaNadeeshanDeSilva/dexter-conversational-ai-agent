#!/bin/bash

# Deploy Lambda Function for Dexter AI Agent
# This script creates or updates a Lambda function using the ECR image

set -e  # Exit on any error

# Disable AWS CLI pager to prevent script blocking
export AWS_PAGER=""

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
FUNCTION_NAME="${FUNCTION_NAME:-dexter-ai-agent}"
REPO_NAME="${REPO_NAME:-dexter-ai-agent}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME"
IMAGE_URI="$ECR_URI:$IMAGE_TAG"

echo "🚀 Deploying Dexter AI Agent to AWS Lambda"
echo "Function Name: $FUNCTION_NAME"
echo "Region: $AWS_REGION"
echo "Image URI: $IMAGE_URI"

# Check if function already exists
if aws lambda get-function --function-name "$FUNCTION_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "📝 Function $FUNCTION_NAME already exists. Updating..."
    
    # Update function code
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --image-uri "$IMAGE_URI" \
        --region "$AWS_REGION"
    
    echo "✅ Function code updated successfully!"
    
    # Wait for function update to complete before updating configuration
    echo "⏳ Waiting for function update to complete..."
    aws lambda wait function-updated --function-name "$FUNCTION_NAME" --region "$AWS_REGION"
    echo "✅ Function update completed!"
else
    echo "🆕 Creating new Lambda function..."
    
    # Create IAM role if it doesn't exist
    ROLE_NAME="dexter-lambda-execution-role"
    ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
    
    echo "🔧 Setting up IAM role..."
    
    # Check if role exists
    if ! aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
        echo "📝 Creating IAM role: $ROLE_NAME"
        
        # Create trust policy
        cat > /tmp/trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
        
        # Create role
        aws iam create-role \
            --role-name "$ROLE_NAME" \
            --assume-role-policy-document file:///tmp/trust-policy.json
        
        # Attach basic execution policy
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # Wait for role to be available
        echo "⏳ Waiting for IAM role to be available..."
        aws iam wait role-exists --role-name "$ROLE_NAME"
        
        echo "✅ IAM role created successfully!"
        
        # Clean up temp file
        rm /tmp/trust-policy.json
    else
        echo "✅ IAM role already exists"
    fi
    
    # Create Lambda function
    aws lambda create-function \
        --function-name "$FUNCTION_NAME" \
        --package-type Image \
        --code ImageUri="$IMAGE_URI" \
        --role "$ROLE_ARN" \
        --region "$AWS_REGION" \
        --timeout 300 \
        --memory-size 1024 \
        --description "Dexter Conversational AI Agent with Memory" \
        --environment 'Variables={ENVIRONMENT=production,LOG_LEVEL=INFO}'
    
    echo "✅ Lambda function created successfully!"
fi

# Update function configuration
echo "🔧 Updating function configuration..."
aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --region "$AWS_REGION" \
    --timeout 300 \
    --memory-size 1024 \
    --environment 'Variables={ENVIRONMENT=production,LOG_LEVEL=INFO}'

echo "✅ Function configuration updated!"

# Display function details
echo ""
echo "📋 Function Details:"
FUNCTION_ARN=$(aws lambda get-function --function-name "$FUNCTION_NAME" --region "$AWS_REGION" --query 'Configuration.FunctionArn' --output text)
echo "Function ARN: $FUNCTION_ARN"
echo "Function Name: $FUNCTION_NAME"
echo "Region: $AWS_REGION"

# Test the function
echo ""
read -p "🧪 Do you want to test the function? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Testing Lambda function..."
    
    # Create test event for health check
    cat > /tmp/test-event.json << EOF
{
    "version": "2.0",
    "routeKey": "GET /health",
    "rawPath": "/health",
    "rawQueryString": "",
    "headers": {
        "content-type": "application/json",
        "host": "localhost"
    },
    "requestContext": {
        "http": {
        "method": "GET",
        "path": "/health",
        "protocol": "HTTP/1.1",
        "sourceIp": "127.0.0.1",
        "userAgent": "aws-cli/2.x"
        }
    },
    "body": null,
    "isBase64Encoded": false
}
EOF
    
    aws lambda invoke \
        --function-name "$FUNCTION_NAME" \
        --region "$AWS_REGION" \
        --cli-binary-format raw-in-base64-out \
        --payload fileb:///tmp/test-event.json \
        --log-type Tail \
        /tmp/lambda-response.json \
        --query 'LogResult' --output text | base64 --decode
    
    echo "📄 Function response:"
    cat /tmp/lambda-response.json | jq -r '.body // .'
    
    # Clean up temp files
    rm /tmp/test-event.json /tmp/lambda-response.json
fi

echo ""
echo "🎉 Lambda deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Set up environment variables for your databases (MongoDB, Pinecone, OpenAI API keys)"
echo "2. Create API Gateway if you want HTTP endpoints"
echo "3. Test your endpoints"
echo ""
echo "🔧 To update environment variables:"
echo "aws lambda update-function-configuration --function-name $FUNCTION_NAME --region $AWS_REGION --environment Variables='{KEY1=value1,KEY2=value2}'"
