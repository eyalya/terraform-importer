from terraform_importer.providers.base_provider import BaseProvider
from typing import List, Dict, Any, Optional, Callable
import requests
import json
import string
import logging

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

# BitbucketDfraustProvider
class BitbucketDfraustProvider(BaseProvider):
    """
    A class for managing Bitbucket resources, including deployments, deployment variables, 
    and repository variables. Provides utilities for paginated API requests and UUID retrieval.

    Attributes:
        username (str): The Bitbucket username for authentication.
        password (str): The Bitbucket app password for authentication.
        workspace (Optional[str]): The Bitbucket workspace (optional).
        base_url (str): The base URL for Bitbucket's API.
        session (requests.Session): A persistent session for making authenticated API calls.
    """

    def __init__(self, auth_config: Dict, provider_name: str = "bitbucket"):
        """
        Initializes the BitbucketImporter with authentication credentials and workspace.

        Args:
            username (str): The Bitbucket username for authentication.
            password (str): The Bitbucket app password for authentication.
            workspace (Optional[str]): The Bitbucket workspace. Defaults to None.
        """
        super().__init__()
        self.__name__ = provider_name

        self.username = auth_config["expressions"]["username"]
        self.password = auth_config["expressions"]["password"]
        # self.workspace = workspace
        self.base_url = f"https://api.bitbucket.org/2.0/repositories/"
        self.session = requests.Session()
        self.auth = (self.username, self.password)
        self._resources_dict = {
            "bitbucket_deployment" : self.bitbucket_deployment,
            "bitbucket_deployment_variable" : self.bitbucket_deployment_variable,
            "bitbucket_repository_variable" : self.bitbucket_repository_variable,
        }
        self.headers = {
            "Accept": "application/json"
        }
        self.check_auth()
        
    def check_auth(self):
        """
        Performs a basic authentication check by making a request to the Bitbucket API.
        
        Raises:
            ValueError: If authentication fails or credentials are invalid.
        """
        try:
            response = self.run_command(self.base_url)
            
            # Check for successful authentication
            if response.status_code == 200:
                print("Authentication successful!")
            else:
                raise ValueError(f"Authentication failed: {response.status_code} - {response.reason}")
        except requests.RequestException as e:
            raise ValueError(f"Authentication check failed: {e}")

    def run_command(self, url):
        return self.session.get(
            url,
            auth=self.auth,
            headers=self.headers
        )
    
    def get_all_results(self, func: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieves all pages of results from a paginated Bitbucket API.

        Args:
            func (Callable): The function to call for each page of results.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            List[Dict[str, Any]]: A combined list of results from all pages.
        """
        results = []
        resp_json, url = func(*args, **kwargs)
        page_num = 1
        
        while resp_json["values"]:
            cleaned = url.rstrip(string.digits)
            url = cleaned + str(page_num)
            page_num += 1
            resp_json, url = func(*args, **kwargs, url=url)
            results += resp_json["values"]

        global_logger.debug(json.dumps(json.loads(json.dumps(results)), sort_keys=True, indent=4, separators=(",", ": ")))
        return results

    def get_variable_uuid(self, repository_name: str, variable: str, deployment_uuid: Optional[str] = None,) -> Optional[str]:
        """
        Retrieves the UUID for a specific deployment variable in a repository.

        Args:
            repository_name (str): The name of the Bitbucket repository.
            deployment_uuid (str): The uuid of the deployment.
            variable (str): The name of the deployment variable.

        Returns:
            Optional[str]: The UUID of the deployment variable, or None if not found.
        """
        envs = self.get_all_results(self.list_deployment_variables_uuid, repository_name, deployment_uuid=deployment_uuid)
        try:
            for item in envs:
                if item.get("key") == variable:
                    return item["uuid"]
        except KeyError:
            global_logger.error(f"Response dont have values and has:")
            global_logger.error(json.dumps(json.loads(envs), sort_keys=True, indent=4, separators=(",", ": ")))
        return None

    def list_deployment_variables_uuid(
        self, repository_name: str, deployment_uuid: Optional[str] = None, url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists deployment variables for a specific repository and deployment.

        Args:
            repository_name (str): The name of the Bitbucket repository.
            deployment_uuid (Optional[str]): The UUID of the deployment. Defaults to None.
            url (Optional[str]): A custom URL for the API request. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of deployment variables with their UUIDs.
        """
        if not url:
            global_logger.debug(f"url: {url}")
            if deployment_uuid:
                global_logger.debug("Get deployment variable")
                url = f"{self.base_url}/{repository_name}/deployments_config/environments/{deployment_uuid}/variables?page=0"
            else:
                global_logger.debug("Get repository variable")
                url = f"{self.base_url}/{repository_name}/pipelines_config/variables/?page=0"

        try:
            response = self.run_command(url)
            
            # Check for successful authentication
            if response.status_code == 200:
               global_logger.debug("Get Variables")
               resp_json = response.json()
            else:
                global_logger.error(f"Request failed: {response.status_code} - {response.reason}")
                return None, None
        except requests.RequestException as e:
            global_logger.error(f"Request failed: {e}")
        
        global_logger.debug(json.dumps(resp_json, sort_keys=True, indent=4, separators=(",", ": ")))
        return resp_json, url

    def get_deployment_uuid(self, repository_name: str, deployment: str) -> Optional[str]:
        """
        Retrieves the UUID for a specific deployment in a repository.

        Args:
            repository_name (str): The name of the Bitbucket repository.
            deployment (str): The name of the deployment.

        Returns:
            Optional[str]: The UUID of the deployment, or None if not found.
        """
        url = f"{self.base_url}/{repository_name}/environments/"

        # headers = {
        # "Accept": "application/json",
        # "Content-Type": "application/json"
        # }

        try:
            response = self.run_command(url)
            
            # Check for successful authentication
            if response.status_code == 200:
               global_logger.debug("Get Variables")
               resp_json = response.json()
            else:
                global_logger.error(f"Request failed: {response.status_code} - {response.reason}")
                return None
        except requests.RequestException as e:
            global_logger.error(f"Request failed: {e}")
        
        global_logger.debug(json.dumps(resp_json, sort_keys=True, indent=4, separators=(",", ": ")))

        envs = json.loads(response.text)
        
        try:
            for item in envs["values"]:
                if item.get("slug") == deployment:
                    return item["uuid"]
        except KeyError:
            global_logger.error(f"Response dont have values and has:")
            global_logger.error(json.dumps(json.loads(envs), sort_keys=True, indent=4, separators=(",", ": ")))
        return None

    def bitbucket_deployment(self, resource_block: Dict[str, Any]) -> str:
        """
        Generates the import block for a Bitbucket deployment resource.

        Args:
            resource_block (Dict[str, Any]): The resource block from the Terraform configuration.

        Returns:
            str: The import block for the Bitbucket deployment.
        """
        deployment_name = resource_block['change']['after']['name']
        repository = resource_block['change']['after']['repository']
        id = self.get_deployment_uuid(repository, deployment_name)
        if id:
            return f"{repository}:{id}"
        return None
        
    def bitbucket_deployment_variable(self, resource_block: Dict[str, Any]) -> str:
        """
        Generates the import block for a Bitbucket deployment variable resource.

        Args:
            resource_block (Dict[str, Any]): The resource block from the Terraform configuration.

        Returns:
            str: The import block for the Bitbucket deployment variable.
        """
        try:
            variable_name = resource_block['change']['after']['key']
            deployment = resource_block['change']['after']['deployment']
            parts = deployment.split(":")
            repository_name = parts[0]
            deployment_id = parts[1]
            id = self.get_variable_uuid(repository_name, variable_name, deployment_id)
            return f"{deployment}/{id}"
        except KeyError:
            global_logger.debug(f"Deployment not creates")
        return None    

    def bitbucket_repository_variable(self, resource_block: Dict[str, Any]) -> str:
        """
        Generates the import block for a Bitbucket repository variable resource.

        Args:
            resource_block (Dict[str, Any]): The resource block from the Terraform configuration.

        Returns:
            str: The import block for the Bitbucket repository variable.
        """
        variable_name = resource_block['change']['after']['key']
        repository_name = resource_block['change']['after']['repository']
        id = self.get_variable_uuid(repository_name, variable_name)
        if id:
            return f"{repository_name}/{variable_name}/{id}"
        return None
