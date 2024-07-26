from botocore.exceptions import ClientError

def handle_eks_cluster(session, account_name, region):
    client = session.client('eks', region_name=region)
    cluster_data = []

    try:
        paginator = client.get_paginator('list_clusters')
        # Iterate over all EKS clusters
        for page in paginator.paginate():
            for cluster_name in page['clusters']:
                try:
                    cluster = client.describe_cluster(name=cluster_name)['cluster']
                    tags = client.list_tags_for_resource(resourceArn=cluster['arn'])['tags']
                    cluster_data.append({
                        'Cluster Name': cluster['name'],
                        'Status': cluster['status'],
                        'Kubernetes Version': cluster['version'],
                        'endpoint': cluster['endpoint'],
                        'Tags': tags,
                        'Account': account_name,
                        'Region': region,
                        'Account': account_name
                    })
                except ClientError as e:
                    print(f"Error describing cluster {cluster_name}: {e}")
    except ClientError as e:
        print(f"Error listing clusters: {e}")

    return cluster_data