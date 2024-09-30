import requests, os 
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import csv

load_dotenv()

# Open the .env file and pull credentials
client_secret = os.getenv("client_secret")
if client_secret is None:
    killScript()
client_id = os.getenv("client_id")

# Replace these with your actual credentials
# CLIENT_ID = 'your_client_id'
# CLIENT_SECRET = 'your_client_secret'
TOKEN_URL = 'https://apigtwb2c.us.dell.com/auth/oauth/v2/token'
#DELL_API_URL = 'https://apigtwb2c.us.dell.com/PROD/sbil/v3/warranty/tags'
DELL_API_URL = 'https://apigtwb2c.us.dell.com/PROD/sbil/eapi/v5/asset-entitlements'

def get_oauth_token(client_id, client_secret):
    """
    Function to retrieve OAuth2 token from Dell API.
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(TOKEN_URL, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret))
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        return token
    else:
        raise Exception(f"Failed to get OAuth token: {response.status_code}, {response.text}")

def get_warranty_info(token, serial_tags):
    """
    Function to query Dell API for warranty info for multiple Serial Tags.
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    warranty_info_list = []
    
    for tag in serial_tags:
        response = requests.get(f"{DELL_API_URL}/{tag}", headers=headers)
        if response.status_code == 200:
            warranty_data = response.json()
            print(f"Warranty info for {tag}: {warranty_data}")
            
            # Add data to the list for CSV output
            warranty_info_list.append({
                'Serial Tag': tag,
                'Warranty Info': warranty_data
            })
        else:
            print(f"Failed to fetch warranty info for {tag}: {response.status_code}, {response.text}")
    
    # Save the results to a CSV file
    save_to_csv(warranty_info_list)

def save_to_csv(warranty_info_list, file_name='warranty_info.csv'):
    """
    Function to save warranty info to a CSV file.
    """
    keys = warranty_info_list[0].keys()  # Get headers from the first dictionary
    with open(file_name, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(warranty_info_list)
    print(f"Warranty information saved to {file_name}")

if __name__ == '__main__':
    # List of serial tags to query
    serial_tags = []
    
    try:
        # Get OAuth token
        token = get_oauth_token(client_id, client_secret)
        
        # Fetch warranty information for multiple tags and save to CSV
        get_warranty_info(token, serial_tags)
    
    except Exception as e:
        print(f"An error occurred: {e}")