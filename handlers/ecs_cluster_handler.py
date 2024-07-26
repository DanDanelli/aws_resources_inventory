from botocore.exceptions import ClientError

def handle_ecs_cluster(session, account_name, region):
    client = session.client('ecs', region_name=region)
    cluster_data = []

    try:
        cluster_details = client.describe_clusters()
    except ClientError as e:
        print(f"Error describing clusters: {e}")
        return []

    # Iterate over all clusters in the region
    for cluster in cluster_details['clusters']:
        try:
            cluster_tags_response = client.list_tags_for_resource(resourceArn=cluster['clusterArn'])
            cluster_tags = {tag['key']: tag['value'] for tag in cluster_tags_response['tags']}
        except ClientError as e:
            print(f"Error listing tags for cluster {cluster['clusterArn']}: {e}")
            cluster_tags = {}

        try:
            services = client.list_services(cluster=cluster['clusterName'])['serviceArns']
        except ClientError as e:
            print(f"Error listing services for cluster {cluster['clusterName']}: {e}")
            services = []

        service_data = []
        
        # Iterate over all services in the cluster
        for service_arn in services:
            service_name = service_arn.split('/')[-1]
            try:
                service = client.describe_services(cluster=cluster['clusterName'], services=[service_name])['services'][0]
                service_tags_response = client.list_tags_for_resource(resourceArn=service['serviceArn'])
                service_tags = {tag['key']: tag['value'] for tag in service_tags_response['tags']}
            except ClientError as e:
                print(f"Error describing service {service_name} in cluster {cluster['clusterName']}: {e}")
                continue

            service_data.append({
                'Service Name': service['serviceName'],
                'Status': service['status'],
                'Task Definition': service['taskDefinition'],
                'Desired Count': service['desiredCount'],
                'Running Count': service['runningCount'],
                'Pending Count': service['pendingCount'],
                'Launch Type': service['launchType'],
                'Tags': service_tags
            })

        cluster_data.append({
            'Cluster Name': cluster['clusterName'],
            'Cluster Status': cluster['status'],
            'Cluster Running Tasks Count': cluster['runningTasksCount'],
            'Cluster Active Services Count': cluster['activeServicesCount'],
            'Services': service_data,
            'Tags': cluster_tags,
            'Region': region,
            'Account': account_name
        })

    return cluster_data