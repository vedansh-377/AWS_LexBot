#!/bin/bash

echo "Installing dependencies..."
pip install --upgrade pip setuptools
pip install -r requirements.txt -t lib

echo "Zipping deployment package..."
cd lib || { echo "Error: Could not change to 'lib' directory"; exit 1; }
zip -r9 ../deployment_package.zip .
cd ..

echo "Checking if Lambda function exists..."
FUNCTION_NAME="github-to-lambda-demo"
FUNCTION_EXISTS=$(aws lambda list-functions --query "Functions[?FunctionName=='$FUNCTION_NAME'].FunctionName" --output text --region us-east-1)

if [ -z "$FUNCTION_EXISTS" ]; then
  echo "Creating new Lambda function..."
  aws lambda create-function --function-name "$FUNCTION_NAME" --runtime python3.11 --handler lambda.handler --role arn:aws:iam::003261238302:role/Lambda --zip-file fileb://deployment_package.zip --region us-east-1 --timeout 1000
else
  echo "Updating existing Lambda function..."
  aws lambda update-function-code --function-name "$FUNCTION_NAME" --zip-file fileb://deployment_package.zip --region us-east-1
fi

echo "Invoking Lambda function..."
aws lambda invoke --function-name "$FUNCTION_NAME" --payload '{}' output.txt --region us-east-1
cat output.txt  # Display the Lambda output

echo "DONE!!"