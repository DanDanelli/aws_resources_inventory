import boto3
from botocore.exceptions import ClientError

def handle_sqs(region):
    sqs_client = boto3.client('sqs', region_name=region)
    sqs_data = []

    try:
        # List all queues
        queues_response = sqs_client.list_queues()
        queue_urls = queues_response.get('QueueUrls', [])
        
        # Iterate over each queue
        for queue_url in queue_urls:
            try:
                # Fetch queue attributes
                attributes_response = sqs_client.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['All']
                )
                attributes = attributes_response['Attributes']
                
                # Fetch queue tags
                tags_response = sqs_client.list_queue_tags(QueueUrl=queue_url)
                tags = tags_response.get('Tags', {})
                
                sqs_data.append({
                    'Queue URL': queue_url,
                    'Attributes': attributes,
                    'Tags': tags,
                    'Region': region
                })
            except ClientError as error:
                print(f"Error retrieving attributes or tags for queue {queue_url}: {error}")
    except ClientError as error:
        print(f"Error listing SQS queues: {error}")
        return []

    return sqs_data