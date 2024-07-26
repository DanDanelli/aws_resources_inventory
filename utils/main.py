import json
import os
import pandas as pd
import boto3
from botocore import exceptions
import logging

# List the accounts in the master account organization
def list_accounts(master_account, role_arn):
    # Use the assume_role_and_create_session function to create a session
    session_tg = assume_role_and_create_session(master_account,role_arn)
    # Use the session to create a client for the AWS Organizations service
    client_tg = session_tg.client('organizations')

    # Create a paginator for the list_accounts operation
    paginator_tg = client_tg.get_paginator('list_accounts')

    # Initialize an empty list to hold the accounts
    accounts = []

    # Iterate over each page of results and add the accounts to the list
    for page in paginator_tg.paginate():
        accounts.extend([{'Id': account['Id'], 'Name': account['Name'], 'Status': account['Status']} for account in page['Accounts']])

    return accounts

# Assume a role in the account and create a session
def assume_role_and_create_session(resource_account_id, role_name):
    try:
        # Assume the role in the account
        sts_client = boto3.client('sts')
        assumed_role_object = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{resource_account_id}:role/{role_name}",
            RoleSessionName='AssumeRoleSession'
        )

        # Create a session with the assumed role's credentials
        session = boto3.Session(
            aws_access_key_id=assumed_role_object['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumed_role_object['Credentials']['SecretAccessKey'],
            aws_session_token=assumed_role_object['Credentials']['SessionToken']
        )

        return session

    except exceptions.BotoCoreError as e:
        logging.error(f"Could not assume role {role_name} in account {resource_account_id}: {e}")
        return None

    except exceptions.ClientError as e:
        logging.error(f"Client error while assuming role {role_name} in account {resource_account_id}: {e}")
        return None

# Define the handlers for the resources
def define_handler_functions(instructions, resource):
    json_file = open(instructions)
    json_content = json.load(json_file)
    type = ''
    module = ''
    function = ''
    for item in json_content['resource_types']:
        if item.get('resource') == resource:
            resource = item.get('resource')
            type = item.get('type')
            if type == 'None':
                module = __import__(f'handlers.{resource}_handler', fromlist=[f'handle_{resource}'])
                function = f'handle_{resource}'
            else:
                module = __import__(f'handlers.{resource}_{type}_handler', fromlist=[f'handle_{resource}_{type}'])
                function = f'handle_{resource}_{type}'
    json_file.close()

    return (getattr(module,function))

# Get the resource types from the JSON file
def define_resource_types(instructions):
    resource_type_list = []
    json_file = open(instructions)
    resource = ''
    type = ''
    json_content = json.load(json_file)
    for i in json_content['resource_types']:
        resource = i.get('resource')
        type = i.get('type')
        if type == 'None':
            resource_type_list.append(f'{resource}')
        else:
            resource_type_list.append(f'{resource}:{type}')
    json_file.close()
    return (resource_type_list)

# Write the data to an Excel file
def write_document(data, filename, resource_type):
    def sanitize_sheet_name(sheet_name):
        invalid_chars = ":\\/?*[]"
        for char in invalid_chars:
            sheet_name = sheet_name.replace(char, "_")
        return sheet_name[:31]  # Truncate to 31 characters
    
    if not any(data.values()):
        return
    
    filepath = filename
    try:
        if os.path.exists(filepath):
            mode = 'a'
            # Open the Excel file in append mode and write the data to the appropriate sheet
            with pd.ExcelWriter(filepath, engine='openpyxl', mode=mode, if_sheet_exists='overlay') as writer:
                for resource_type, resource_data in data.items():
                    if resource_data:
                        sanitized_sheet_name = sanitize_sheet_name(resource_type)
                        df = pd.DataFrame(resource_data)
                        if sanitized_sheet_name in writer.sheets:
                            # Append the data to the existing sheet
                            if writer.sheets[sanitized_sheet_name].max_row == 1:
                                df.to_excel(writer, sheet_name=sanitized_sheet_name, startrow=writer.sheets[sanitized_sheet_name].max_row, index=False)
                            # If the sheet already has data, append the new data below the existing data
                            else:
                                df.to_excel(writer, sheet_name=sanitized_sheet_name, startrow=writer.sheets[sanitized_sheet_name].max_row, index=False, header=False)
                        else:
                            df.to_excel(writer, sheet_name=sanitized_sheet_name, index=False)
                        resource_data.clear()
        else:
            mode = 'w'
            # Create a new Excel file and write the data to the appropriate sheet
            with pd.ExcelWriter(filepath, engine='openpyxl', mode=mode) as writer:
                for resource_type, resource_data in data.items():
                    if resource_data:
                        sanitized_sheet_name = sanitize_sheet_name(resource_type)
                        df = pd.DataFrame(resource_data)
                        df.to_excel(writer, sheet_name=sanitized_sheet_name, index=False)
                        resource_data.clear()
    except Exception as e:
        print(f"An error occurred while writing to the Excel file: {e}")