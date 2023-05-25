import os
from msal import ConfidentialClientApplication
import requests
from pprint import pprint
from dotenv import load_dotenv


# load sensitive information
load_dotenv()


client_id = os.getenv('CLIENT_ID')
thumbprint = os.getenv('THUMBPRINT')
tenant_id = os.getenv('TENANT_ID')
organization = os.getenv('ORGANIZATION')
site = os.getenv('SITE')
authority = f'https://login.microsoftonline.com/{tenant_id}'


# Sharepoint requires certificate authentification
# To generate a cert & key use:
# $ openssl req -newkey rsa:2048 -new -nodes -x509 -days 90 -keyout key.pem -out cert.pem
# Remember to load the cert to the add, get the thumbprint 
# And API Permissions set for Application Sharepoint Sites.Read.All 
with open('key.pem') as f:
    private_key = str(f.read())

cert = {
    'private_key': private_key,
    'thumbprint': thumbprint,
}

msal_app = ConfidentialClientApplication(
    client_id=client_id,
    authority=authority,
    client_credential=cert,
)

sharepoint_scopes = [f'https://{organization}.sharepoint.com/.default']

result = msal_app.acquire_token_for_client(scopes=sharepoint_scopes)
access_token = result.get('access_token')
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json;odata=verbose',
    'Content-Type': 'application/json',
}

sharepoint_base_url = f'https://{organization}.sharepoint.com/sites/{site}'
sharepoint_url = f'{sharepoint_base_url}/_api/web/sitegroups'
response = requests.get(url=sharepoint_url, headers=headers)

print(response.status_code)
pprint(response.json())
