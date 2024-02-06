import os
import requests
import boto3
import time
import json

def get_latest_github_release(owner, repo, folder):
    # GitHub API endpoint to list contents of a folder in a repository
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}"

    # Make a GET request to the GitHub API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        contents = response.json()

        # Filter out only files (not directories)
        files = [item for item in contents if item['type'] == 'file']

        # Get the latest file based on the last modified time
        latest_file = max(files, key=lambda x: x['last_modified'], default=None)

        if latest_file:
            # Return the download URL and file name of the latest file
            return latest_file['download_url'], latest_file['name']

    return None, None

def create_github_release(owner, repo, tag_name, release_name, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "tag_name": tag_name,
        "name": release_name,
        "body": "Release created automatically after successful LexV2 import."
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code == 201

def main():
    # AWS service clients
    lex_models_client = boto3.client('lexv2-models')

    # GitHub repository details
    owner = 'vedansh-377'
    repo = 'AWS_LexBot'
    folder = 'lexzip'
    github_token = os.getenv('GITHUB_TOKEN')

    # Get the download URL and name of the latest Lex bot ZIP file from GitHub
    download_url, zip_name = get_latest_github_release(owner, repo, folder)

    if not download_url:
        print("No Lex bot ZIP file found in the specified GitHub folder. Exiting.")
        return 1

    # Create an upload URL
    create_upload_url_response = lex_models_client.create_upload_url()
    upload_url = create_upload_url_response['uploadUrl']
    import_id = create_upload_url_response['importId']
    print(upload_url)
    print(import_id)

    # Download the Lex bot ZIP file from GitHub
    response = requests.get(download_url)
    file_contents = response.content

    # Upload the Lex bot ZIP file to the provided upload URL
    response = requests.put(upload_url, data=file_contents, headers={'Content-Type': 'application/zip'})

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
        # Create a GitHub release with the tag name as the name of the ZIP file
        if create_github_release(owner, repo, zip_name, f"Release {zip_name}", github_token):
            print('LexV2 import completed successfully! GitHub release created.')
            return 0
        else:
            print('Failed to create GitHub release after LexV2 import.')
            return 1
    else:
        print('LexV2 import not yet completed.')
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
