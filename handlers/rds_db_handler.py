from botocore.exceptions import BotoCoreError, ClientError
import re
import boto3

# Function to format the size of the RDS instance
def format_size(gigabytes):
    """Convert gigabytes to a more readable format."""
    if gigabytes < 1024:
        size = float(gigabytes)  # Convert to float to use .is_integer()
        return f"{gigabytes} GB" if size.is_integer() else f"{gigabytes:.2f} GB"
    else:
        size = gigabytes / 1024
        return f"{size:.0f} TB" if size.is_integer() else f"{size:.2f} TB"

# Function to validate the RDS instance identifier
def is_valid_identifier(instance_id):
    # Regex to match AWS's naming conventions for DBInstanceIdentifier
    pattern = r'^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$'
    return bool(re.match(pattern, instance_id))

def handle_rds_db(region):
    rds_client = boto3.client('rds', region_name=region)
    db_data = []
    marker = None

    try:
        while True:
            if marker:
                instance_details = rds_client.describe_db_instances(Marker=marker)
            else:
                instance_details = rds_client.describe_db_instances()

            db_instances = instance_details['DBInstances']
            # Iterate over all RDS instances
            for instance in db_instances:
                try:
                    tags_response = rds_client.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
                    tags = tags_response.get('TagList', [])
                except (BotoCoreError, ClientError) as tag_error:
                    print(f"Error retrieving tags for {instance['DBInstanceIdentifier']}: {tag_error}")
                    tags = []

                db_data.append({
                    'Name': instance['DBInstanceIdentifier'],
                    'Engine': instance['Engine'],
                    'Engine Version': instance['EngineVersion'],
                    'Class': instance['DBInstanceClass'],
                    'Allocated Storage': format_size(instance['AllocatedStorage']),
                    'BackupRetentionPeriod': f"{instance['BackupRetentionPeriod']} days",
                    'Status': instance['DBInstanceStatus'],
                    'Endpoint': instance['Endpoint']['Address'],
                    'Port': instance['Endpoint']['Port'],
                    'Tags': tags,
                    'Region': region
                })

            # Update marker for next iteration
            marker = instance_details.get('Marker')
            if not marker:
                break  # Exit loop if no more instances to fetch

        return db_data

    except (BotoCoreError, ClientError) as error:
        if error.response['Error']['Code'] == 'DBInstanceNotFound':
            print(f"RDS instance {instance['DBInstanceIdentifier']} not found.")
        else:
            print(f"Error getting details for RDS instance {instance['DBInstanceIdentifier']}: {error}")
        return []