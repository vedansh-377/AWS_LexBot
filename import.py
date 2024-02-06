import os
import boto3
import time
import json

import requests

def get_latest_zip_from_folder(folder):
    # List all files in the specified folder
    files = os.listdir(folder)

    # Filter out only ZIP files
    zip_files = [file for file in files if file.endswith('.zip')]

    # Sort the ZIP files based on their names (assuming they have version numbers in their names)
    sorted_zip_files = sorted(zip_files, reverse=True)

    if sorted_zip_files:
        # Return the path to the latest ZIP file
        return os.path.join(folder, sorted_zip_files[0])

    return None

def main():
    # AWS service clients
    lex_models_client = boto3.client('lexv2-models')

    # Folder containing Lex bot ZIP files
    lexzip_folder = 'LexZip'

    # Get the path to the latest Lex bot ZIP file
    latest_zip_path = get_latest_zip_from_folder(lexzip_folder)

    if not latest_zip_path:
        print("No Lex bot ZIP file found in the specified folder. Exiting.")
        return 1

    # Create an upload URL
    create_upload_url_response = lex_models_client.create_upload_url()
    upload_url = create_upload_url_response['uploadUrl']
    import_id = create_upload_url_response['importId']
    print(upload_url)
    print(import_id)

    # Upload the Lex bot ZIP file to the provided upload URL
    with open(latest_zip_path, 'rb') as file_data:
        response = requests.put(upload_url, data=file_data, headers={'Content-Type': 'application/zip'})

    # Wait for the upload to be processed
    time.sleep(10)

    # Start the bot import
    import_bot_response = lex_models_client.start_import(
        importId=import_id,
        resourceSpecification={
            'botImportSpecification': {
                'botName': 'Abook',
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

    if describe_import_response['importStatus'] == 'Completed':
        print('LexV2 import completed successfully!')
        return 0
    else:
        print('LexV2 import not yet completed.')
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
