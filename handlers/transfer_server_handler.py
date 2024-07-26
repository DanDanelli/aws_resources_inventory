def handle_transfer_server(session, account_name, region):
    transfer_client = session.client('transfer', region_name=region)
    transfer_data = []
    marker = None
    try:
        while True:
            if marker:
                servers = transfer_client.list_servers(Marker=marker)
            else:
                servers = transfer_client.list_servers()

            # Iterate over all Transfer Family servers
            for server in servers['Servers']:
                server_id = server['ServerId']
                server_details = transfer_client.describe_server(ServerId=server_id)
                server_state = server_details['Server']['State']
                server_arn = server_details['Server']['Arn']
                
                tags_response = transfer_client.list_tags_for_resource(Arn=server_arn)
                tags = tags_response.get('Tags', [])
                
                transfer_data.append({
                    'Server ID': server_id,
                    'State': server_state,
                    'Tags': tags,
                    'Region': region,
                    'Account': account_name,
                })

            marker = servers.get('NextMarker')
            if not marker:
                break

        return transfer_data

    except transfer_client.exceptions.ServiceError as error:
        print(f"Error getting details for Transfer Family servers: {error}")
        return []