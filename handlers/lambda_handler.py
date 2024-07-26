import botocore

def handle_lambda(session, account_name, region):
    
    client = session.client('lambda', region_name=region)
    lambda_data = []
    # Function to format the size of the Lambda function
    def format_size(bytes):
        """Convert bytes to a more readable format."""
        if bytes < 1024:
            return f"{bytes} bytes"
        elif bytes < 1024**2:
            return f"{bytes / 1024:.2f} KB"
        elif bytes < 1024**3:
            return f"{bytes / (1024**2):.2f} MB"
        elif bytes < 1024**4:
            return f"{bytes / (1024**3):.2f} GB"
        else:
            return f"{bytes / (1024**4):.2f} TB"
    
    try:
        marker = None
        while True:
            if marker:
                function_details = client.list_functions(Marker=marker)
            else:
                function_details = client.list_functions()
            
            # Iterate over all Lambda functions
            for function in function_details['Functions']:
                tags_response = client.list_tags(Resource=function['FunctionArn'])
                tags = tags_response.get('Tags', {})
                
                lambda_data.append(
                    {
                    'Function Name': function['FunctionName'],
                    'Runtime': function['Runtime'],
                    'Memory Size': format_size(function['MemorySize']),
                    'CodeSize': format_size(function['CodeSize']),
                    'Tags': tags,
                    'Region': region,
                    'Account': account_name,
                    }
                )
            
            if 'NextMarker' in function_details:
                marker = function_details['NextMarker']
            else:
                break

        return lambda_data
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as error:
        print(f"Error getting details for Lambda function {function['FunctionName']}: {error}")
        return []