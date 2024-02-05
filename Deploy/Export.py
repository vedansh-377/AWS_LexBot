import boto3
import json
import os
import requests
import time

def export_lexv2_model(bot_id, bot_version, region_name='us-east-1'):
    client = boto3.client('lexv2-models', region_name=region_name)
    
    response = client.create_export(
        resourceSpecification={
            'botExportSpecification': {
                'botId': bot_id,
                'botVersion': bot_version
            }
        },
        fileFormat='LexJson'
    )
    
    return response

def describe_lexv2_export_job(export_job_id):
    client = boto3.client('lexv2-models')
    
    response = client.describe_export(
        exportId=export_job_id
    )
    
    return response

def store_exported_model_in_artifacts(content, file_name, artifacts_dir):
    # Create a directory to store artifacts if it doesn't exist
    if not os.path.exists(artifacts_dir):
        os.makedirs(artifacts_dir)

    # Construct the file path for the exported model
    file_path = os.path.join(artifacts_dir, file_name)

    # Write the exported model to the file
    with open(file_path, 'wb') as file:
        file.write(content.content)

    print(f"Exported model stored in artifacts: {file_path}")

def main():
    # Replace 'your_model_id' with the actual LexV2 model ID
    bot_id = 'IQU3BOJ9BH' 
    bot_version = '4'
    
    # Export the LexV2 model
    export_response = export_lexv2_model(bot_id, bot_version)
    print("Export Response:", export_response)

    time.sleep(20)
    
    # Describe the export job
    export_job_id = export_response['exportId']
    describe_export_response = describe_lexv2_export_job(export_job_id)
    print("Describe Export Job Response:", describe_export_response)
    
    # Check if the export job is complete
    if describe_export_response['exportStatus'] == 'Completed':
        # Retrieve the download URL of the exported model
        download_url = describe_export_response['downloadUrl']
        response = requests.get(download_url)

        if response.status_code == 200:
            # Specify the file name for the downloaded file
            file_name = f'version{bot_version}'

            # Define the directory to store artifacts in Jenkins
            artifacts_dir = 'jenkins_artifacts'

            # Store the exported model in the Jenkins artifacts
            store_exported_model_in_artifacts(response, file_name, artifacts_dir)

if __name__ == "__main__":
    main()
