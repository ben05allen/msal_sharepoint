from msal import ConfidentialClientApplication
import requests


class FileInfo:

    def __init__(self, 
                 name: str, 
                 path: str, 
                 item_id: str, 
                 modified_date: str, 
                 url: str) -> None:
        
        self.name = name
        self.path = path
        self.item_id = item_id
        self.modified_date = modified_date
        self.url = url

    def __repr__(self) -> str:
        return (f'FileInfo(name={self.name}, path={self.path}, item_id={self.item_id}, '
                f'modified_date={self.modified_date}, url={self.url})')


class SharePoint:

    def __init__(self, 
                 tenant_id: str, 
                 client_id: str, 
                 organization: str,
                 private_key: str,
                 thumbprint: str) -> None:
        
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.organization = organization
        self.private_key = private_key
        self.thumbprint = thumbprint
        
        self.access_token = None
        self.headers = None
        self.authority = f'https://login.microsoftonline.com/{self.tenant_id}'
        self.sharepoint_scopes = [f'https://{self.organization}.sharepoint.com/.default']
        self.base_url = f'https://{self.organization}.sharepoint.com'

    def get_access_token(self) -> str:
        msal_app = ConfidentialClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            client_credential={
                'private_key': self.private_key,
                'thumbprint': self.thumbprint,
            },
        )
        result = msal_app.acquire_token_for_client(scopes=self.sharepoint_scopes)
        return result.get('access_token')
    
    def set_headers(self) -> None:
        access_token = self.get_access_token()
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json;odata=verbose',
            'Content-Type': 'application/json',
        }

    def get_sharepoint_site(self, site_id: str):
        if self.headers is None:
            self.set_headers()
        sitegroups_url = f'{self.base_url}/sites/{site_id}/_api/web/sitegroups'
        response = requests.get(url=sitegroups_url, headers=self.headers)

        if response.ok:
            return response.json()
        return {'Bad request': response.status_code}
    
    def get_files(self, 
                  drive_id: str, 
                  root_child: str, 
                  folder_name: str) -> list[dict]:
        
        if self.headers is None:
            self.set_headers()
        
        # drive_url = (f'{self.base_url}/drives/{drive_id}/root:/'
        #                 f'{root_child}/{folder_name}:/children')


        drive_url = (f"{self.base_url}/sites/ClientData-Accelerate/site/_api/web/lists")
        response = requests.get(url=drive_url, headers=self.headers)

        print(drive_url)
        print(response.status_code)

        if not response.ok:
            raise FileNotFoundError(f'Folder {folder_name} not found')
       
        # if response.json() and response.json().get('value'):
        #     return [FileInfo(
        #         name = file["name"], 
        #         path = file["parentReference"]["path"].split('root:/')[1],
        #         item_id = file["id"],
        #         modified_date = file["lastModifiedDateTime"],
        #         url = file["@microsoft.graph.downloadUrl"])
        #             for file in response.json()['value']]
        
        return []
    
    def delete_file(self, drive_id: str, file: FileInfo) -> None:
        if self.headers is None:
            self.set_headers()
        
        delete_url = f'{self.base_url}/drives/{drive_id}/items/{file.item_id}'
        response = requests.delete(url=delete_url, headers=self.headers)
        if not response.ok:
            raise FileNotFoundError(f'File {file.name} not found')

    @staticmethod
    def download_file(file: FileInfo, local_root: str) -> None:
        response = requests.get(file.url)
        with open(f'{local_root}/{file.path}/{file.name}', 'wb') as f:
            f.write(response.content)

    @staticmethod
    def read_file(file: FileInfo) -> bytes:
        response = requests.get(file.url)
        return response.content
        
      