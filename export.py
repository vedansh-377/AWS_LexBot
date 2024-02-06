import boto3
import json
import requests
from github import Github
import time
import os


def handler(event, context):
    # Replace 'your_model_id' with the actual LexV2 model ID
    bot_id = 'IQU3BOJ9BH'
    bot_version = '9'

    github_token = os.environ.get('GITHUB_TOKEN')
    repo_name = 'AWS_LexBot'
    github_branch = 'main'  # or any other branch
    github_directory = 'lexzip'  # Specify the directory in the GitHub repo


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

            # Authenticate with GitHub using a personal access token
            g = Github(github_token)

            # Get the GitHub repository
            # repo = g.get_repo(repo_name)

            # Store the exported model in the GitHub repository
            store_exported_model_in_github(repo_name, github_branch, github_directory, file_name, response.content)

            # Add any additional logic or processing here

            return {
                'statusCode': 200,
                'body': json.dumps('LexV2 export and storage in GitHub completed successfully!')
            }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps('LexV2 export failed or not yet completed.')
        }


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


def store_exported_model_in_github(repo, branch, directory, file_name, content):
    # Get the contents of the existing directory in the GitHub repo
    contents = repo.get_contents(directory, ref=branch)

    # Create a new file in the GitHub repo
    repo.create_file(f'{directory}/{file_name}', f'Add {file_name}', contents, branch=branch)

    print(f"Exported model stored in GitHub repo: {directory}/{file_name}")


# Rest of your functions remain unchanged

if __name__ == "__main__":
    handler(None, None)  # Call the handler function for testing
