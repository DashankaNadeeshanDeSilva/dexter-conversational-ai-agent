#!/bin/bash

# Setup API Gateway for Dexter AI Agent Lambda Function
# This script creates an API Gateway REST API and connects it to the Lambda function

set -e  # Exit on any error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
FUNCTION_NAME="${FUNCTION_NAME:-dexter-ai-agent}"
API_NAME="${API_NAME:-dexter-ai-api}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Setting up API Gateway for Dexter AI Agent"
echo "API Name: $API_NAME"
echo "Function: $FUNCTION_NAME"
echo "Region: $AWS_REGION"

# Get Lambda function ARN
FUNCTION_ARN=$(aws lambda get-function --function-name "$FUNCTION_NAME" --region "$AWS_REGION" --query 'Configuration.FunctionArn' --output text)
echo "Function ARN: $FUNCTION_ARN"

# Check if API already exists
API_ID=$(aws apigateway get-rest-apis --region "$AWS_REGION" --query "items[?name=='$API_NAME'].id" --output text)

if [ -n "$API_ID" ] && [ "$API_ID" != "None" ]; then
    echo "✅ API Gateway $API_NAME already exists with ID: $API_ID"
else
    echo "🆕 Creating API Gateway: $API_NAME"
    
    # Create REST API
    API_ID=$(aws apigateway create-rest-api \
        --name "$API_NAME" \
        --description "API Gateway for Dexter AI Agent" \
        --region "$AWS_REGION" \
        --query 'id' \
        --output text)
    
    echo "✅ API Gateway created with ID: $API_ID"
fi

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --region "$AWS_REGION" --query 'items[?path==`/`].id' --output text)
echo "Root Resource ID: $ROOT_RESOURCE_ID"

# Create proxy resource for Lambda integration
echo "🔧 Setting up proxy integration..."

# Check if proxy resource exists
PROXY_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --region "$AWS_REGION" --query "items[?pathPart=='{proxy+}'].id" --output text)

if [ -z "$PROXY_RESOURCE_ID" ] || [ "$PROXY_RESOURCE_ID" == "None" ]; then
    # Create proxy resource
    PROXY_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id "$API_ID" \
        --parent-id "$ROOT_RESOURCE_ID" \
        --path-part '{proxy+}' \
        --region "$AWS_REGION" \
        --query 'id' \
        --output text)
    
    echo "✅ Proxy resource created with ID: $PROXY_RESOURCE_ID"
else
    echo "✅ Proxy resource already exists with ID: $PROXY_RESOURCE_ID"
fi

# Create ANY method for proxy resource
echo "🔧 Setting up ANY method..."
aws apigateway put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$PROXY_RESOURCE_ID" \
    --http-method ANY \
    --authorization-type NONE \
    --region "$AWS_REGION" >/dev/null

# Create Lambda integration
echo "🔧 Setting up Lambda integration..."
aws apigateway put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$PROXY_RESOURCE_ID" \
    --http-method ANY \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$FUNCTION_ARN/invocations" \
    --region "$AWS_REGION" >/dev/null

# Add Lambda permission for API Gateway
echo "🔧 Adding Lambda permission for API Gateway..."
aws lambda add-permission \
    --function-name "$FUNCTION_NAME" \
    --statement-id "api-gateway-invoke-$API_ID" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$AWS_REGION:$AWS_ACCOUNT_ID:$API_ID/*/*" \
    --region "$AWS_REGION" >/dev/null 2>&1 || echo "Permission already exists"

# Create root resource method for health check
echo "🔧 Setting up root resource methods..."

# Create GET method for root resource (health check)
aws apigateway put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$ROOT_RESOURCE_ID" \
    --http-method GET \
    --authorization-type NONE \
    --region "$AWS_REGION" >/dev/null

# Create integration for root GET method
aws apigateway put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$ROOT_RESOURCE_ID" \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$FUNCTION_ARN/invocations" \
    --region "$AWS_REGION" >/dev/null

# Deploy API
echo "🚀 Deploying API..."
aws apigateway create-deployment \
    --rest-api-id "$API_ID" \
    --stage-name prod \
    --region "$AWS_REGION" >/dev/null

echo "✅ API deployed to 'prod' stage!"

# Display API details
API_URL="https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/prod"
echo ""
echo "📋 API Gateway Details:"
echo "API ID: $API_ID"
echo "API URL: $API_URL"
echo "Health Check: $API_URL/health"
echo "Chat Endpoint: $API_URL/chat"

# Test the API
echo ""
read -p "🧪 Do you want to test the API? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Testing health endpoint..."
    curl -s "$API_URL/health" | jq '.' || echo "Health check failed - this might be expected if environment variables are not set"
fi

echo ""
echo "🎉 API Gateway setup complete!"
echo ""
echo "📋 Important URLs:"
echo "Health Check: $API_URL/health"
echo "Chat Endpoint: $API_URL/chat"
echo "API Documentation: $API_URL/docs"
echo ""
echo "🔧 Next Steps:"
echo "1. Set up environment variables in Lambda for your databases"
echo "2. Test all endpoints"
echo "3. Set up custom domain if needed"
