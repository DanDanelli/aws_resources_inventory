import botocore.exceptions

def format_size(megabytes):
    """Convert megabytes to a more readable format."""
    if megabytes < 1:
        size = megabytes * 1024
        return f"{size:.0f} KB" if size.is_integer() else f"{size:.2f} KB"
    elif megabytes < 1024:
        return f"{megabytes:.0f} MB" if megabytes.is_integer() else f"{megabytes:.2f} MB"
    elif megabytes < 1024**2:
        size = megabytes / 1024
        return f"{size:.0f} GB" if size.is_integer() else f"{size:.2f} GB"
    else:
        size = megabytes / 1024**2
        return f"{size:.0f} TB" if size.is_integer() else f"{size:.2f} TB"

def handle_ec2_instance(session, account_name, region):
    client = session.client('ec2', region_name=region)
    instance_type_cache = {}
    instance_data = []

    try:
        # Iterate over all instances in the region
        for page in client.get_paginator('describe_instances').paginate():
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    # Fetch instance type details if not already cached
                    if instance['InstanceType'] not in instance_type_cache:
                        instance_type_details = client.describe_instance_types(InstanceTypes=[instance['InstanceType']])['InstanceTypes'][0]
                        instance_type_cache[instance['InstanceType']] = instance_type_details
                    volume_info = []
                    # Fetch volume details for each block device
                    for mapping in instance.get('BlockDeviceMappings', []):
                        # Check if the block device has an EBS volume
                        if 'Ebs' in mapping:
                            volume_id = mapping['Ebs']['VolumeId']
                            volume_details = client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
                            volume_size = volume_details['Size']  # Size in GiB
                            is_root = mapping.get('DeviceName') == instance.get('RootDeviceName')
                            volume_info.append({
                                'Volume ID': volume_id, 
                                'Size (GiB)': volume_size,
                                'Type': 'Root' if is_root else 'EBS'
                            })

                    # Attempt to find a 'Name' tag for the instance
                    instance_name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), None)

                    # If no 'Name' tag is found, use a default name or the instance ID
                    if not instance_name:
                        instance_name = f"Unnamed Instance ({instance['InstanceId']})"
                    instance_data.append({
                        'ID': instance['InstanceId'],
                        'Name': instance_name,
                        'Type': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'Private IP': instance.get('PrivateIpAddress', ''),
                        'Public IP': instance.get('PublicIpAddress', ''),
                        'vCPUs': instance_type_details['VCpuInfo']['DefaultVCpus'],
                        'Memory (MiB)': format_size(instance_type_details['MemoryInfo']['SizeInMiB']),
                        'Volumes': volume_info,  # Updated to include volume IDs and sizes
                        'Tags': instance.get('Tags', []),
                        'Region': region,
                        'Account': account_name,
                    })
    except botocore.exceptions.ClientError as e:
        print(f"An error occurred: {e}")

    return instance_data