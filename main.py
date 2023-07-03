from dotenv import load_dotenv
import os
from pprint import pprint
from sharepoint import SharePoint

# load sensitive information
load_dotenv()
client_id = os.getenv('CLIENT_ID')
thumbprint = os.getenv('THUMBPRINT')
tenant_id = os.getenv('TENANT_ID')
organization = os.getenv('ORGANIZATION')
site_id = os.getenv('SITE_ID')
drive_id = os.getenv('DRIVE_ID')


# Sharepoint requires certificate authentification
# To generate a cert & key use:
# $ openssl req -newkey rsa:2048 -new -nodes -x509 -days 90 -keyout key.pem -out cert.pem
# Remember to load the cert to the add, get the thumbprint 
# And API Permissions set for Application Sharepoint Sites.Read.All 
with open('key.pem') as f:
    private_key = str(f.read())

sp = SharePoint(
    tenant_id=tenant_id,
    client_id=client_id,
    organization=organization,
    private_key=private_key,
    thumbprint=thumbprint,
)

# site_response = sp.get_sharepoint_site(site_id)
# pprint(site_response)


drive_response = sp.get_files(drive_id=site_id, 
                              root_child='Accelerate', 
                              folder_name='Booster')
pprint(drive_response)