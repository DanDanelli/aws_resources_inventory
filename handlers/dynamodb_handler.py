from botocore.exceptions import ClientError

def handle_dynamodb(session, account_name, region):
    dynamodb_client = session.client('dynamodb', region_name=region)
    dynamodb_data = []

    try:
        # Initialize paginator for list_tables
        paginator = dynamodb_client.get_paginator('list_tables')
        # Iterate over all DynamoDB tables
        for page in paginator.paginate():
            for table_name in page['TableNames']:
                try:
                    table_details = dynamodb_client.describe_table(TableName=table_name)
                    table_status = table_details['Table']['TableStatus']
                    # Fetch tags for the table
                    tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=table_details['Table']['TableArn'])
                    tags = tags_response.get('Tags', {})
                    # Append table data once, including tags
                    dynamodb_data.append({
                        'Table Name': table_name,
                        'Status': table_status,
                        'Tags': tags,
                        'Account': account_name,
                        'Region': region
                    })
                except ClientError as error:
                    print(f"Error getting details for DynamoDB table {table_name}: {error}")
        return dynamodb_data

    except ClientError as error:
        print(f"Error listing DynamoDB tables: {error}")
        return []