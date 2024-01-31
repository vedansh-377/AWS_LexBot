import os
import requests
import boto3
import time
import json

def get_latest_s3_key(bucket):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket)
    # Get the latest object key based on the last modified time
    latest_object = max(response.get('Contents', []), key=lambda x: x['LastModified'], default=None)
    return latest_object['Key'] if latest_object else None

def handler(event, context):
    # AWS service clients
    lex_models_client = boto3.client('lexv2-models')

    # Replace with your S3 bucket
    s3_bucket = 'my-lexv2-import-bucket'

    # Get the latest S3 key
    s3_key = get_latest_s3_key(s3_bucket)

    if not s3_key:
        print("No objects found in the S3 bucket. Exiting.")
        return {
            'statusCode': 500,
            'body': json.dumps('No objects found in the S3 bucket.')
        }

    # Create an upload URL
    create_upload_url_response = lex_models_client.create_upload_url()
    upload_url = create_upload_url_response['uploadUrl']
    import_id = create_upload_url_response['importId']
    print(upload_url)
    print(import_id)

    # Download the Lex bot ZIP file from S3
    local_file_path = '/tmp/exported_bot.zip'
    s3_client = boto3.client('s3')
    s3_client.download_file(s3_bucket, s3_key, local_file_path)

    # Upload the Lex bot ZIP file to the provided upload URL
    with open(local_file_path, 'rb') as file_data:
        response = requests.put(upload_url, data=file_data, headers={'Content-Type': 'application/zip'})

    # Wait for the upload to be processed
    time.sleep(10)

    # Start the bot import
    import_bot_response = lex_models_client.start_import(
        importId=import_id,
        resourceSpecification={
            'botImportSpecification': {
                'botName': 'Book',
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
    print("Upload URL:", upload_url)
    print("Import ID:", import_id)
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
