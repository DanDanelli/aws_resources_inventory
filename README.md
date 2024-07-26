
# AWS Resources Inventory

A script that list and describe AWS resources for inventory purpose.


## Documentation

Considering different scenarios:
### Identity Center Multi-Account (branch ident._center-multi_account)
    In this scenario, it will be considered that there is a landing zone consisting of:
        - Master Account (Where the OUs are configured)
        - Operational Account (Responsible for assuming a role in the Linked Accounts and describing the resources)
    Python will assume role from Operational Account, get in Master Account to list all Linked Accounts in Organizations and 
    will enter in each Linked Account listed and describe according with resource filter from the region informed.

  ![image](https://github.com/user-attachments/assets/eff70b76-9c0f-4af7-85ed-418f3cc80dd0)
  ![image](https://github.com/user-attachments/assets/94f4a774-40c0-466d-aa66-9c427773eba9)
## Usage/Examples
### Create Role in Operational Account and Linked Accounts with Trusted Entities (for policy consider AdministratorAccess for test):
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
Configure Operation Account
```bash
  $ cat ~/.aws/credentials
[OPERATION_ACCOUNT]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
region = your_region
```
Execute Python
```bash
  $ python get_inventory.py -h
Usage: get_inventory.py --region <region> --master_account <master_account> --ops_role_name <ops_role_name>
Required Args:
  --region              Specify the AWS region
  --master_account      Specify the master account ID
  --ops_role_name       Specify the role name
  -h, --help            Show this help message and exit
```
