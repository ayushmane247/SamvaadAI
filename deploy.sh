#!/bin/bash
set -e

# Colors for output commands
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting SamvaadAI Full Deployment Automation...${NC}"

# 1. Check Prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"
if ! command -v aws &> /dev/null; then
    echo "aws-cli could not be found. Please install it first."
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo "aws-sam-cli could not be found. Please install it first."
    exit 1
fi
echo -e "${GREEN}Prerequisites found.${NC}"

# 2. Build and Deploy Backend
echo -e "\n${YELLOW}Building AWS SAM application (using containers)...${NC}"
sam build --use-container

echo -e "\n${YELLOW}Deploying backend to AWS...${NC}"
sam deploy \
    --stack-name samvaadai-backend \
    --resolve-s3 \
    --capabilities CAPABILITY_IAM \
    --no-confirm-changeset

# 3. Retrieve Outputs
echo -e "\n${YELLOW}Retrieving Stack Outputs...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name samvaadai-backend \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)

SCHEME_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name samvaadai-backend \
    --query "Stacks[0].Outputs[?OutputKey=='SchemesBucketName'].OutputValue" \
    --output text)

echo -e "${GREEN}API Endpoint: ${API_ENDPOINT}${NC}"
echo -e "${GREEN}S3 Schemes Bucket: ${SCHEME_BUCKET}${NC}"

# 4. Upload Scheme Data to S3
if [ -n "$SCHEME_BUCKET" ] && [ "$SCHEME_BUCKET" != "None" ]; then
    echo -e "\n${YELLOW}Uploading Scheme Data to S3 Bucket...${NC}"
    aws s3 cp docs/ s3://${SCHEME_BUCKET}/maharashtra/ \
        --recursive \
        --exclude "*" \
        --include "*.json"
    echo -e "${GREEN}Scheme Data successfully uploaded.${NC}"
else
    echo -e "\n${YELLOW}Warning: Could not determine S3 Bucket name. Please upload scheme data manually.${NC}"
fi

# 5. Configure Frontend
echo -e "\n${YELLOW}Configuring Frontend Environment Variables...${NC}"
if [ -n "$API_ENDPOINT" ] && [ "$API_ENDPOINT" != "None" ]; then
    echo "VITE_API_URL=${API_ENDPOINT}" > frontend/.env.production
    echo -e "${GREEN}frontend/.env.production successfully generated with API URL.${NC}"
else
    echo -e "\n${YELLOW}Warning: Could not determine API Endpoint. Please configure frontend environment manually.${NC}"
fi

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}Backend Deployment & Configuration Complete! ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "Your backend is live and your scheme data is uploaded."
echo -e "Your frontend has been configured with the correct API URL."
echo -e "\n${YELLOW}Next Steps for Frontend Deployment (AWS Amplify):${NC}"
echo -e "1. Commit these changes (including frontend/.env.production and template.yaml) to your GitHub repository:"
echo -e "   git add ."
echo -e "   git commit -m \"chore: ready for production deployment\""
echo -e "   git push"
echo -e "2. Go to the AWS Amplify Console: https://console.aws.amazon.com/amplify/home"
echo -e "3. Click 'Create new app' -> 'Host web app'."
echo -e "4. Connect GitHub and select the 'frontend' directory as a monorepo."
echo -e "5. Click Deploy! AWS Amplify will handle the rest via amplify.yml."
