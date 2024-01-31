import requests
import boto3
import json
import time

def handler(event, context):
    # AWS service clients
    lex_models_client = boto3.client('lexv2-models')
    s3_client = boto3.client('s3')
    
    # Replace with your S3 bucket
    s3_bucket = 'my-lexv2-export-bucket'
    
    # Get the latest model file
    latest_model = get_latest_model(s3_bucket)
    
    if latest_model:
        # Create an upload URL
        create_upload_url_response = lex_models_client.create_upload_url()
        upload_url = create_upload_url_response['uploadUrl']
        import_id = create_upload_url_response['importId']
        print("Upload URL:", upload_url)
        print("Import ID:", import_id)

        # Directly send the Lex bot ZIP file to the provided upload URL
        with requests.get(latest_model['download_url'], stream=True) as response:
            response.raise_for_status()
            response_data = response.content

        # Upload the Lex bot ZIP file to the provided upload URL
        response = requests.put(upload_url, data=response_data, headers={'Content-Type': 'application/zip'})
        
        # Wait for the upload to be processed
        time.sleep(10)

        # Start the bot import
        import_bot_response = lex_models_client.start_import(
            importId=import_id,
            resourceSpecification={
                'botImportSpecification': {
                    'botName': 'BookhotelBot',
                    'roleArn': 'arn:aws:iam::526222510576:role/aws-service-role/lexv2.amazonaws.com/AWSServiceRoleForLexV2Bots_N3K8T788LA',
                    'dataPrivacy': {'childDirected': False},
                    'idleSessionTTLInSeconds': 600
                }
            },
            mergeStrategy='FailOnConflict'
        )
        
        # Wait for the import to complete
        time.sleep(20)
        
        # Describe the import status
        describe_import_response = lex_models_client.describe_import(importId=import_id)
        
        # Log the import details
        print(import_bot_response)
        print("Import Status:", describe_import_response['importStatus'])
        
        if import_bot_response['importStatus'] == 'Completed':
            return {
                'statusCode': 200,
                'body': json.dumps('LexV2 import completed successfully!')
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('LexV2 import not yet completed.')
            }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps('No exported model found in the S3 bucket.')
        }

def get_latest_model(s3_bucket):
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket)
        latest_model = max(response['Contents'], key=lambda x: x['LastModified'])
        
        return {
            'key': latest_model['Key'],
            'download_url': f"https://{s3_bucket}.s3.amazonaws.com/{latest_model['Key']}"
        }
    except Exception as e:
        print(f"Error retrieving the latest model: {e}")
        return None
