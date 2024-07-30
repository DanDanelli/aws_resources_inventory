
# AWS Resources Inventory

# Prerequisites
- [Python](https://www.python.org/)
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
# Challenge
This script is designed to gather inventory data for various AWS resources. This function is part of a script that 
helps in auditing and managing AWS resources by collecting detailed information about each resource. Additionally, it supports parallel processing to 
efficiently handle large volumes of data across multiple AWS services.
# Branches
- [Identity Center Multi-Account](https://github.com/DanDanelli/aws_resources_inventory/tree/ident._center-multi_account)
- [Standalone Account](https://github.com/DanDanelli/aws_resources_inventory/tree/standalone-account)
# Documentation
Considering different scenarios:
## Identity Center Multi-Account
    In this scenario, it will be considered that there is a landing zone consisting of:
        - Master Account (Where the OUs are configured)
        - Operational Account (Responsible for assuming a role in the Linked Accounts and describing the resources)
    Python will assume role from Operational Account, get in Master Account to list all Linked Accounts in Organizations and 
    will enter in each Linked Account listed and describe according with resource filter from the region informed.

  ![image](https://github.com/user-attachments/assets/eff70b76-9c0f-4af7-85ed-418f3cc80dd0)
  ![image](https://github.com/user-attachments/assets/94f4a774-40c0-466d-aa66-9c427773eba9)
### Usage/Examples
- Create Role in Operational Account and Linked Accounts with Trusted Entities (for policy consider AdministratorAccess for test):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::{OPERATIONAL_ACCOUNT_ID}:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {}
        }
    ]
}
```
- Configure Operation Account
```bash
  $ cat ~/.aws/credentials
[OPERATION_ACCOUNT]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
region = your_region
```
- Execute Python
```bash
  $ python get_inventory.py -h
Usage: get_inventory.py --region <region> --master_account <master_account> --ops_role_name <ops_role_name>
Required Args:
  --region              Specify the AWS region
  --master_account      Specify the master account ID
  --ops_role_name       Specify the role name
  -h, --help            Show this help message and exit
```
#### Output demo
Filtered for search ec2_instance and s3_bucket
![image](https://github.com/user-attachments/assets/b2a0ec26-a99d-4d17-8cf0-986393cb3285)
![image](https://github.com/user-attachments/assets/e0cac08d-d43a-4b8c-893e-19febc0c906d)

## Standalone Account
 In this scenario, it will be considered just a standalone account:
  ![image](https://github.com/user-attachments/assets/01892116-3563-473a-83de-90111b50d529)
### Usage/Examples
- Configure Standalone Account
```bash
  $ cat ~/.aws/credentials
[STANDALONE ACCOUNT]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
region = your_region
```
- Execute Python
```bash
  $ python get_inventory.py -h
Usage: get_inventory.py --region <region>
Required Args:
  --region              Specify the AWS region
  -h, --help            Show this help message and exit
```
#### Output demo
Filtered for search ec2_instance
![image](https://github.com/user-attachments/assets/b34ee5f1-eced-43f5-ab56-7dac43880993)

# Conclusion
The process_resource function is a versatile tool for gathering inventory data across various AWS services. By extending this function to include additional services, you can create a comprehensive inventory management solution for your AWS environment.
