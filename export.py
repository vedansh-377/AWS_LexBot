import os
import boto3
import requests
import time
import base64

def main():
    # Replace 'your_model_id' with the actual LexV2 model ID
    bot_id = 'IQU3BOJ9BH' 
    bot_version = '9'
    
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
            file_name = f'version{bot_version}.zip'
        
            # Store the exported model in GitHub
            store_exported_model_in_github(response.content, file_name)
        
        # Add any additional logic or processing here
        print("LexV2 export and storage in GitHub completed successfully!")
    else:
        print("LexV2 export failed or not yet completed.")

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

def store_exported_model_in_github(content, file_name):
    # Specify GitHub repository details
    repo_owner = 'vedansh-377'
    repo_name = 'AWS_LexBot'
    branch_name = 'main'
    file_path = f'LexZip/{file_name}' 
    github_token = os.environ.get('GITHUB_TOKEN')

    if not github_token:
        print("GitHub token not found in environment variables.")
        return

    # Create the GitHub API URL
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

    # Base64 encode the file content
    encoded_content = base64.b64encode(content).decode('utf-8')

    # Create the request body
    payload = {
        "message": "Add LexV2 model zip file",
        "content": encoded_content,
        "branch": branch_name
    }

    # Add authentication header
    headers = {
        "Authorization": f"token {github_token}"
    }

    # Make the PUT request to upload the file to GitHub
    response = requests.put(url, headers=headers, json=payload)
    print(response)

    if response.status_code == 201:
        print(f"LexV2 model zip file '{file_name}' uploaded to GitHub successfully!")
    else:
        print("Failed to upload LexV2 model zip file to GitHub and latest zip is already there.")

if __name__ == "__main__":
    main()
