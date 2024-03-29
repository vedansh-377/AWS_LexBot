import boto3
import requests
import time


def main():
    # Replace 'your_model_id' with the actual LexV2 model ID
    bot_id = 'V2V5BO42CC'
    bot_version = '2'

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

            # Check if the S3 bucket exists, create it if not
            s3_bucket = 'my-lexv2-export-bucket'
            if not check_s3_bucket_exists(s3_bucket):
                create_s3_bucket(s3_bucket)

            # Store the exported model in the S3 bucket
            store_exported_model_in_s3(response, file_name, s3_bucket)

        # Add any additional logic or processing here

        print('LexV2 export and storage in S3 completed successfully!')
    else:
        print('LexV2 export failed or not yet completed.')


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


def check_s3_bucket_exists(bucket_name):
    s3 = boto3.client('s3')

    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        return False


def create_s3_bucket(bucket_name, region='us-east-1'):
    s3 = boto3.client('s3', region_name=region)

    # For us-east-1, use the default bucket creation without specifying LocationConstraint
    if region == 'us-east-1':
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    print(f"S3 bucket created: {bucket_name} in region: {region}")


def store_exported_model_in_s3(content, file_name, s3_bucket):
    s3 = boto3.client('s3')

    # Convert the response content to bytes
    content_bytes = content.content

    # Upload the exported model to the specified S3 bucket
    s3.put_object(
        Bucket=s3_bucket,
        Key=file_name,
        Body=content_bytes
    )

    print(f"Exported model stored in S3 bucket: {s3_bucket}/{file_name}")


if __name__ == "__main__":
    main()
