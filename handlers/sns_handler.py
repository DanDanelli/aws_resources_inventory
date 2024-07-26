import boto3
import botocore

def handle_sns(session, account_name, region):
    sns_client = session.client('sns', region_name=region)
    sns_data = []

    try:
        # Initialize pagination
        paginator = sns_client.get_paginator('list_topics')
        page_iterator = paginator.paginate()

        # Iterate over each page of topics
        for page in page_iterator:
            for topic in page['Topics']:
                topic_arn = topic['TopicArn']
                
                # Fetch topic attributes
                topic_attributes = sns_client.get_topic_attributes(TopicArn=topic_arn)
                attributes = topic_attributes['Attributes']
                topic_owner = attributes.get('Owner', 'N/A')
                topic_subscriptions_count = attributes.get('SubscriptionsConfirmed', 'N/A')

                # Fetch tags for the topic
                tags_response = sns_client.list_tags_for_resource(ResourceArn=topic_arn)
                tags = tags_response.get('Tags', {})
                
                sns_data.append({
                    'Topic ARN': topic_arn,
                    'Owner': topic_owner,
                    'Subscriptions Count': topic_subscriptions_count,
                    'Tags': tags,
                    'Region': region,
                    'Account': account_name,
                })

        return sns_data

    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as error:
        print(f"Error getting details for SNS topics: {error}")
        return []