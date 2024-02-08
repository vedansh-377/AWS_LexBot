# import base64
import os
import boto3
import time
import requests
import argparse


def get_latest_zip_from_folder(folder):
    # List all files in the specified folder
    files = os.listdir(folder)
    print(files)

    # Filter out only ZIP files
    zip_files = [file for file in files if file.endswith('.zip')]

    # Get the full path for each ZIP file
    zip_files_paths = [os.path.join(folder, file) for file in zip_files]

    # Sort the ZIP files based on their modification time
    sorted_zip_files = sorted(zip_files_paths, key=os.path.getmtime, reverse=True)
    print(sorted_zip_files)

    if sorted_zip_files:
        # Return the path to the latest ZIP file
        return sorted_zip_files[0]

    return None

def create_github_release(owner, repo, tag_name, release_name, github_token, zip_path):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }


# Adjust the download_url to point to the ZIP file within the GitHub Actions workspace
    download_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{os.path.relpath(zip_path, '/home/runner/work/AWS_LexBot/AWS_LexBot/')}"
    body = f"Release created automatically after successful LexV2 import. Download the zip file [here]({download_url}).\n\n"




    body = f"Release created automatically after successful LexV2 import. Download the zip file [here]({download_url}).\n\n"

    data = {
        "tag_name": tag_name,
        "name": release_name,
        "body" : body
    }

    # Send the release creation request
    response = requests.post(url, headers=headers, json=data)
    print(response)
    if response.status_code == 201:
        release_id = response.json()["id"]
        return True
    else:
        print("Failed to create GitHub release:", response.status_code, response.text)
        return False


def main(version=None):
    # AWS service clients
    lex_models_client = boto3.client('lexv2-models')

    # Folder containing Lex bot ZIP files
    lexzip_folder = '/home/runner/work/AWS_LexBot/AWS_LexBot/'

    # If a version is specified, use it
    if version:
        zip_name = f"version{version}"
        latest_zip_path = os.path.join(lexzip_folder, zip_name + '.zip')
        if not os.path.exists(latest_zip_path):
            print(f"Specified version '{version}' not found. Exiting.")
            return 1
    else:
        # Get the path to the latest Lex bot ZIP file
        latest_zip_path = get_latest_zip_from_folder(lexzip_folder)

        if not latest_zip_path:
            print("No Lex bot ZIP file found in the specified folder. Exiting.")
            return 1

        zip_name = os.path.basename(latest_zip_path)

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
        mergeStrategy='Overwrite'
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
        # Create a GitHub release with the tag name as the name of the latest ZIP file
        github_token = os.getenv('GITHUB_TOKEN')
        if create_github_release('vedansh-377', 'AWS_LexBot', zip_name, f"Release {zip_name}", github_token, latest_zip_path):
            print('GitHub release created successfully!')
            return 0
        else:
            print('Failed to create GitHub release or upload zip after LexV2 import.')
            return 1
    else:
        print('LexV2 import not yet completed.')
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run LexV2 import with optional version')
    parser.add_argument('--version', type=str, help='Specify the version to use')
    args = parser.parse_args()
    exit_code = main(args.version)
    exit(exit_code)
