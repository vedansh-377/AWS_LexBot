#!/bin/bash

# Your import logic to migrate and import data from S3
# Example: Migrate data from S3 bucket to another AWS account

# Set the destination bucket name and region
DESTINATION_BUCKET="my-lexv2-import-bucket"
DESTINATION_REGION="us-east-1"


# Create the destination S3 bucket if it doesn't exist
aws s3api create-bucket --bucket $DESTINATION_BUCKET --region $DESTINATION_REGION

# Your migration logic here

# Import data to the destination S3 bucket
aws s3 cp exported_bot.zip s3://$DESTINATION_BUCKET/

echo "Installing dependencies..."
pip install --upgrade pip setuptools
pip install -r requirements.txt -t lib

echo "Zipping deployment package..."
(cd lib && zip -r9 ../deployment_package_1.zip .)
zip -g deployment_package_1.zip IamImport.py

echo "Checking if Lambda function exists..."
FUNCTION_NAME="github-to-lambda-demo"
FUNCTION_EXISTS=$(aws lambda list-functions --query "Functions[?FunctionName=='$FUNCTION_NAME'].FunctionName" --output text --region us-east-1)

if [ -z "$FUNCTION_EXISTS" ]; then
  echo "Creating new Lambda function..."
  aws lambda create-function --function-name "$FUNCTION_NAME" --runtime python3.11 --handler IamImport.handler --role arn:aws:iam::526222510576:role/IamImport --zip-file fileb://deployment_package_1.zip --region us-east-1 --timeout 900
else
  echo "Updating existing Lambda function..."
  aws lambda update-function-code --function-name "$FUNCTION_NAME" --zip-file fileb://deployment_package_1.zip --region us-east-1
fi
sleep 20
echo "Invoking Lambda function..."
aws lambda invoke --function-name "$FUNCTION_NAME" --payload '{}' output.txt --region us-east-1
cat output.txt  # Display the Lambda output
