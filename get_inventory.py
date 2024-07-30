import logging
import getopt
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from botocore.exceptions import ClientError, BotoCoreError
from utils.main import define_handler_functions, define_resource_types
from utils.main import write_document

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the process_resource function
def process_resource(resource, data, region):
    logging.info(f"Start processing resource type {resource} in {region}")
    handler_function = define_handler_functions("resource_types_filter.json", resource.split(':')[0])
    
    if handler_function:
        try:
            data[resource].extend(handler_function(region))
        except Exception as e:
            logging.error(f"Error processing resource {resource} in {region}: {e}")
    else:
        logging.warning(f"No handler function defined for resource type {resource}")

# Define the search_resources function
def search_resources(region):
    filename = './inventory_output/inventory.xlsx'
    data = defaultdict(list)
    try:
        # Assume role in the operations account to get a session
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            resources = define_resource_types("resource_types_filter.json")
            for resource in resources:
                resource_type = resource.split(':')[0]
                futures.append(executor.submit(process_resource, resource, data, region))

            for future in as_completed(futures):
                future.result()
                write_document(data, filename, resource_type)
    except (ClientError, BotoCoreError) as e:
        logging.error(f"AWS error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def print_help():
    print('Usage: get_inventory.py --region <region>')
    print('Required Args:')
    print('  --region              Specify the AWS region')
    print('  -h, --help            Show this help message and exit')

def main(argv):
    region = ''
    try:
        opts, args = getopt.getopt(argv, "h", ["region=", "help"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt == "--region":
            region = arg
    if not region:
        print('Region is required. Usage: get_inventory.py --region <region>')
        sys.exit(2)
    
    search_resources(region)

if __name__ == "__main__":
    main(sys.argv[1:])