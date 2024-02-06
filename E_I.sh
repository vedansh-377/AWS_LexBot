#!/bin/bash

# Set AWS credentials
AWS_ACCESS_KEY_ID="your_access_key"
AWS_SECRET_ACCESS_KEY="your_secret_key"
AWS_DEFAULT_REGION="us-east-1"  # Set your preferred AWS region

# Set GitHub credentials
GITHUB_TOKEN="your_github_token"
GITHUB_REPO="your_github_repo"
GITHUB_BRANCH="main"  # or any other branch
GITHUB_DIRECTORY="lexzip"

# Set other variables
PYTHON_SCRIPT="your_python_script.py"

# Configure AWS CLI
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
aws configure set default.region "$AWS_DEFAULT_REGION"

# Install dependencies
sudo apt-get update
echo "Installing dependencies..."
pip install --upgrade pip setuptools
pip install -r requirements.txt -t lib

# Run Python script with GitHub credentials
python3 "$PYTHON_SCRIPT" "$AWS_ACCESS_KEY_ID" "$AWS_SECRET_ACCESS_KEY" "$AWS_DEFAULT_REGION" "$GITHUB_TOKEN" "$GITHUB_REPO" "$GITHUB_BRANCH" "$GITHUB_DIRECTORY"
