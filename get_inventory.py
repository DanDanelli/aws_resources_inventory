import logging
import getopt
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from botocore.exceptions import ClientError, BotoCoreError
from utils.main import define_handler_functions, define_resource_types, assume_role_and_create_session, list_accounts
from utils.main import write_document

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the process_resource function
def process_resource(resource, session, account, data, region):
    logging.info(f"Start processing resource type {resource} in {region} for account {account['Name']}")
    handler_function = define_handler_functions("resource_types_filter.json", resource.split(':')[0])
    
    if handler_function:
        try:
            data[resource].extend(handler_function(session, account['Name'], region))
        except Exception as e:
            logging.error(f"Error processing resource {resource} in {region} for account {account['Id']}: {e}")
    else:
        logging.warning(f"No handler function defined for resource type {resource}")

# Define the search_resources function
def search_resources(master_account, ops_role_name, region):
    accounts = list_accounts(master_account,ops_role_name)
    filename = './inventory_output/inventory.xlsx'
    data = defaultdict(list)

    try:
        # Assume role in the operations account to get a session
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for account in accounts:
                resources = define_resource_types("resource_types_filter.json")
                for resource in resources:
                    session = assume_role_and_create_session(account['Id'], ops_role_name)
                    if session is None:
                        continue
                    resource_type = resource.split(':')[0]
                    futures.append(executor.submit(process_resource, resource, session, account, data, region))

            for future in as_completed(futures):
                future.result()
                write_document(data, filename, resource_type)
    except (ClientError, BotoCoreError) as e:
        logging.error(f"AWS error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def print_help():
    print('Usage: get_inventory.py --region <region> --master_account <master_account> --ops_role_name <ops_role_name>')
    print('Required Args:')
    print('  --region              Specify the AWS region')
    print('  --master_account      Specify the master account ID')
    print('  --ops_role_name       Specify the role name')
    print('  -h, --help            Show this help message and exit')

def main(argv):
    region = ''
    master_account = ''
    ops_role_name = ''
    try:
        opts, args = getopt.getopt(argv, "h", ["region=", "master_account=", "ops_role_name=", "help"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt == "--region":
            region = arg
        elif opt == "--master_account":
            master_account = arg
        elif opt == "--ops_role_name":
            ops_role_name = arg
    if not region or not master_account or not ops_role_name:
        print('Region, master_account, and ops_role_name are required. Usage: get_inventory.py --region <region> --master_account <master_account> --ops_role_name <ops_role_name>')
        sys.exit(2)
    
    search_resources(master_account, ops_role_name, region)

if __name__ == "__main__":
    main(sys.argv[1:])