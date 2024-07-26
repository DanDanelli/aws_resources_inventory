from botocore.exceptions import ClientError

def handle_apigateway_api(session, account_name, region):
    client = session.client('apigateway', region_name=region)
    apigw_data = []

    try:
        # Initialize paginator for get_rest_apis
        paginator = client.get_paginator('get_rest_apis')
        for page in paginator.paginate():
            for apigtw in page['items']:
                tags = client.get_tags(resourceArn=apigtw['id'])['tags']
                apigw_data.append({
                    'REST API ID': apigtw['id'],
                    'Name': apigtw['name'],
                    'Description': apigtw.get('description', 'No description available'),
                    'Tags': tags,
                    'Region': region,
                    'Account': account_name
                })
    except ClientError as e:
        print(f"Error retrieving API Gateway data: {e}")

    return apigw_data