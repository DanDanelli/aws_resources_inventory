from botocore.exceptions import ClientError
import boto3

def handle_cloudfront(region):
    cloudfront_client = boto3.client('cloudfront', region_name=region)
    cloudfront_data = []

    try:
        paginator = cloudfront_client.get_paginator('list_distributions')
        # Iterate over all CloudFront distributions
        for page in paginator.paginate():
            for distribution in page['DistributionList'].get('Items', []):
                tags_response = cloudfront_client.list_tags_for_resource(Resource=distribution['ARN'])
                tags = tags_response.get('Tags', {}).get('Items', [])
                tags_dict = {tag['Key']: tag['Value'] for tag in tags}

                cloudfront_data.append({
                    'Distribution ID': distribution['Id'],
                    'Domain Name': distribution['DomainName'],
                    'Status': distribution['Status'],
                    'Enabled': distribution['Enabled'],
                    'Tags': tags_dict,
                    'Region': region
                })
    except ClientError as error:
        print(f"Error retrieving CloudFront distributions: {error}")
        return []

    return cloudfront_data