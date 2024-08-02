import boto3
from concurrent.futures import ThreadPoolExecutor
import botocore
import os
from datetime import datetime, timedelta

# Function to format the size of the S3 bucket
def format_size(bytes):
    """Convert bytes to a more readable format."""
    if bytes < 1024:
        return f"{bytes} bytes"
    elif bytes < 1024**2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024**3:
        return f"{bytes / (1024**2):.2f} MB"
    elif bytes < 1024**4:
        return f"{bytes / (1024**3):.2f} GB"
    else:
        return f"{bytes / (1024**4):.2f} TB"

def process_bucket(bucket, region):
    try:
        client = boto3.client('s3', region_name=region)
        
        # Initialize total size and object count
        total_size = 0
        total_objects = 0
        storage_class = 'STANDARD'
        
        # Create a paginator for listing all versions of objects in the bucket
        paginator = client.get_paginator('list_object_versions')
        page_iterator = paginator.paginate(Bucket=bucket['Name'])
        
        # Iterate over each page of object versions
        for page in page_iterator:
            # Accumulate sizes from object versions
            if "Versions" in page:
                for version in page['Versions']:
                    total_size += version['Size']
                    total_objects += 1
                    storage_class = version.get('StorageClass', 'STANDARD')  # Default to 'STANDARD' if not present
            # Optionally, count delete markers if needed
            # if "DeleteMarkers" in page:
            #     for delete_marker in page['DeleteMarkers']:
            #         total_objects += 1
        
        # Convert total size to a human-readable format
        formatted_size = format_size(total_size)
        
        # Fetch tags for the bucket
        try:
            bucket_details = client.get_bucket_tagging(Bucket=bucket['Name'])
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                bucket_details = {'TagSet': [{'Key': 'No Tags', 'Value': 'No Tags'}]}
            else:
                raise e
        
        
        # Fetch lifecycle configuration for the bucket
        try:
            lifecycle_configuration = client.get_bucket_lifecycle_configuration(Bucket=bucket['Name'])
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                lifecycle_configuration = {'Rules': [{'ID': 'No Lifecycle', 'Status': 'No Lifecycle'}]}
            else:
                raise e
        
        # Check for cross-region replication configuration
        try:
            replication_configuration = client.get_bucket_replication(Bucket=bucket['Name'])
            replication_status = 'Enabled'
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ReplicationConfigurationNotFoundError':
                replication_status = 'Not Configured'
            else:
                raise e

        bucket_location = client.get_bucket_location(Bucket=bucket['Name'])
        bucket_data = {
            'Name': bucket['Name'],
            'StorageClass': storage_class,
            'Lifecycle': lifecycle_configuration['Rules'],
            'Size': formatted_size,
            'Objects': total_objects,
            'ReplicationStatus': replication_status,
            'Tags': bucket_details['TagSet'],
            'Region': bucket_location['LocationConstraint'] if 'LocationConstraint' in bucket_location else 'no region specified'
        }

        return bucket_data
    
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError, Exception) as error:
        print(f"Error processing bucket {bucket['Name']}: {error}")
        return None

def handle_s3_bucket(region):
    session = boto3.Session(region_name=region)
    client = session.client('s3')
    credentials = session.get_credentials().get_frozen_credentials()
    all_buckets = client.list_buckets()

    new_env = os.environ.copy()
    new_env['AWS_ACCESS_KEY_ID'] = credentials.access_key
    new_env['AWS_SECRET_ACCESS_KEY'] = credentials.secret_key
    new_env['AWS_SESSION_TOKEN'] = credentials.token

    bucket_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_bucket, bucket, region) for bucket in all_buckets['Buckets']]
        for future in futures:
            result = future.result()
            if result:
                bucket_data.append(result)

    return bucket_data