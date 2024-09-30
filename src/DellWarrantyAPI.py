import argparse
import os
import csv
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

readMe = '''This is a script to collect warranty info for Serial tags provided either via .csv file, 
included in command line or from within the script itself. The results will print out to the console 
a current list of attributes from the Dell Warranty API. It takes a .csv file and will retrieve the 
existing warranty info.

Usage:
 python DellWarrantyAPI.py -f <yourSerialTags.csv> -r <file path> -h [opens help file]

**Note this script will not return any results if you have not put your Dell client_id and client_secret
  in the .env file

The .env file will need to be populated with your Dell API key and a Client Id for the Serial Tags 
you wish to interrogate.

Parameters:
  -f <yourSerialTags.csv> : The path to the CSV file that contains the serial tags.
  -r <outputName.csv>     : Optional. Name of the file you want to save. If "-r" is used and no name is given,
                            filename will be "warranty_data.csv".
  -h                      : Help option that opens this ReadMe.      

Example:
  python DellWarrantyAPI.py -f "MySerialTags.csv" -r "WarrantyInfo.csv" 

Notes:
 * In Windows, use double quotes ("") to enter command line parameters containing spaces.
 * This script was built for Python 3.11.0.
 * Depending on your operating system, the command to start python can be either "python" or "python3". 

Required Python modules:
  Requests      : http://docs.python-requests.org
  python-dotenv : https://pypi.org/project/python-dotenv/

After installing Python, you can install these additional modules using pip with the following commands:
pip install requests
pip install python-dotenv

Depending on your operating system, the command can be "pip3" instead of "pip".
'''

# Print Help File
def print_help():
    print(readMe)

# Option Function to kill script
def kill_script(reason=None):
    if reason is None:
        print_help()
        sys.exit()
    else:
        print("ERROR: %s" % reason)
        sys.exit()

# Read in Service Tags from CSV file
def read_csv_to_dict(file_path):
    print("File path: ",file_path)
    """Reads a CSV file into a list of dictionaries."""
    if not file_path.lower().endswith('.csv'):
        kill_script("Error: The provided file is not a CSV file.")

    if not os.path.isfile(file_path):
        kill_script(f"Error: The file '{file_path}' does not exist.")

    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except Exception as e:
        kill_script(f"Error reading the file: {e}")
    print("Service tags from file: ",data) 
    return data

# Fetch warranty information from Dell API
def get_warranty_data(client_id, client_secret, service_tags):
    # Get access token
    auth_url = 'https://apigtwb2c.us.dell.com/auth/oauth/v2/token'
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    auth_response = requests.post(auth_url, data=auth_data)
    if auth_response.status_code != 200:
        kill_script("Error: Failed to authenticate with Dell API.")

    access_token = auth_response.json().get('access_token')
    if not access_token:
        kill_script("Error: No access token received from Dell API.")

    warranty_url = 'https://apigtwb2c.us.dell.com/PROD/sbil/eapi/v5/asset-entitlements'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'servicetags': ','.join([tag['serviceTag'] for tag in service_tags])
    }

    warranty_response = requests.get(warranty_url, headers=headers, params=params)
    if warranty_response.status_code != 200:
        kill_script("Error: Failed to retrieve warranty data from Dell API.")

    return warranty_response.json()

# Function to create .csv file from warranty data
def create_csv_from_json(json_data, output_path):
    def handle_none(value, default="N/A"):
        return value if value is not None else default

    # Write the CSV file
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow([
            'id', 'serviceTag', 'orderBuid', 'shipDate', 'productCode',
            'localChannel', 'productLineDescription', 'productLobDescription',
            'countryCode', 'entitlement_itemNumber', 'entitlement_startDate',
            'entitlement_endDate', 'entitlement_entitlementType',
            'entitlement_serviceLevelCode', 'entitlement_serviceLevelDescription'
        ])

        # Write each row of data
        for entry in json_data:
            for entitlement in entry.get('entitlements', []):
                writer.writerow([
                    handle_none(entry.get('id')),
                    handle_none(entry.get('serviceTag')),
                    handle_none(entry.get('orderBuid')),
                    handle_none(entry.get('shipDate')),
                    handle_none(entry.get('productCode')),
                    handle_none(entry.get('localChannel')),
                    handle_none(entry.get('productLineDescription')),
                    handle_none(entry.get('productLobDescription')),
                    handle_none(entry.get('countryCode')),
                    handle_none(entitlement.get('itemNumber')),
                    handle_none(entitlement.get('startDate')),
                    handle_none(entitlement.get('endDate')),
                    handle_none(entitlement.get('entitlementType')),
                    handle_none(entitlement.get('serviceLevelCode')),
                    handle_none(entitlement.get('serviceLevelDescription'))
                ])
    print(f"Output written to: {output_path}")

def main():
    # Load credentials from .env file
    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")

    if not client_id or not client_secret:
        kill_script("API Key Client ID or Secret Missing")

    # Set up argument parser
    parser = argparse.ArgumentParser(description="A script to process a CSV file of Serial Tags and generate a CSV file of Warranty Information.")
    parser.add_argument('-f', '--file', type=str, help="The path to the CSV file to use for serial tags.", required=True)
    parser.add_argument('-r', '--result', type=str, help="The path and filename to store the program output.", default='warranty_data.csv')
    args = parser.parse_args()

    # Read the CSV file into a dictionary
    data = read_csv_to_dict(args.file)

    if not data:
        kill_script("No Service Tags in the provided CSV file.")

    # Get Warranty Info from Dell API
    warranty_info = get_warranty_data(client_id, client_secret, data)

    # Write the output to the specified file
    create_csv_from_json(warranty_info, args.result)

if __name__ == '__main__':
    main()
