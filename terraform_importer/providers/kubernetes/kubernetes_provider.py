from terraform_importer.providers.base_provider import BaseProvider
from typing import List, Dict, Any, Optional, Tuple
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

class KubernetesProvider(BaseProvider):
    """
    A provider for managing Kubernetes resources. Supports authentication via kubeconfig,
    in-cluster configuration, or explicit configuration.
    
    Attributes:
        api_client: The Kubernetes API client instance.
        core_v1: Core V1 API client for namespaces, pods, services, etc.
        apps_v1: Apps V1 API client for deployments, statefulsets, daemonsets, etc.
        networking_v1: Networking V1 API client for ingresses.
        rbac_authorization_v1: RBAC V1 API client for roles and bindings.
        storage_v1: Storage V1 API client for persistent volume claims.
    """

    def __init__(self, auth_config: Dict, provider_name: str = "kubernetes"):
        """
        Initializes the Kubernetes provider with authentication configuration.
        
        Args:
            auth_config (Dict): Configuration dictionary containing authentication details.
                Expected keys:
                - 'expressions': Dict containing:
                  - 'config_path' (Optional[str]): Path to kubeconfig file
                  - 'context' (Optional[str]): Kubernetes context to use
                  - 'in_cluster' (Optional[bool]): Whether to use in-cluster config
            provider_name (str): Name of the provider instance. Defaults to "kubernetes".
        """
        super().__init__()
        self.__name__ = provider_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize Kubernetes client
        self.api_client = self._initialize_client(auth_config["expressions"])
        self.core_v1 = client.CoreV1Api(self.api_client)
        self.apps_v1 = client.AppsV1Api(self.api_client)
        self.networking_v1 = client.NetworkingV1Api(self.api_client)
        self.rbac_authorization_v1 = client.RbacAuthorizationV1Api(self.api_client)
        self.storage_v1 = client.StorageV1Api(self.api_client)
        
        # Resource mapping dictionary
        self._resources_dict = {
            "kubernetes_namespace": self.kubernetes_namespace,
            "kubernetes_pod": self.kubernetes_pod,
            "kubernetes_deployment": self.kubernetes_deployment,
            "kubernetes_service": self.kubernetes_service,
            "kubernetes_config_map": self.kubernetes_config_map,
            "kubernetes_secret": self.kubernetes_secret,
            "kubernetes_persistent_volume_claim": self.kubernetes_persistent_volume_claim,
            "kubernetes_stateful_set": self.kubernetes_stateful_set,
            "kubernetes_daemon_set": self.kubernetes_daemon_set,
            "kubernetes_ingress": self.kubernetes_ingress,
            "kubernetes_service_account": self.kubernetes_service_account,
            "kubernetes_role": self.kubernetes_role,
            "kubernetes_role_binding": self.kubernetes_role_binding,
            "kubernetes_cluster_role": self.kubernetes_cluster_role,
            "kubernetes_cluster_role_binding": self.kubernetes_cluster_role_binding,
        }
        
        # Test connection
        self._verify_connection()
    
    def _initialize_client(self, auth_config: Dict) -> client.ApiClient:
        """
        Initializes the Kubernetes API client based on authentication configuration.
        
        Args:
            auth_config (Dict): Authentication configuration dictionary.
            
        Returns:
            client.ApiClient: Initialized Kubernetes API client.
            
        Raises:
            ValueError: If authentication configuration is invalid.
            FileNotFoundError: If kubeconfig file is not found.
        """
        try:
            in_cluster = auth_config.get("in_cluster", False)
            config_path = auth_config.get("config_path")
            context = auth_config.get("config_context")
            
            if in_cluster:
                # Use in-cluster configuration (when running inside a pod)
                self.logger.info("Using in-cluster Kubernetes configuration")
                config.load_incluster_config()
            elif config_path:
                # Use explicit kubeconfig path - expand ~ to home directory
                expanded_path = os.path.expanduser(config_path)
                if not os.path.exists(expanded_path):
                    raise FileNotFoundError(f"Kubeconfig file not found: {expanded_path}")
                self.logger.info(f"Loading Kubernetes config from: {expanded_path}")
                config.load_kube_config(config_file=expanded_path, context=context)
            else:
                # Use default kubeconfig location (~/.kube/config)
                self.logger.info("Using default Kubernetes configuration")
                config.load_kube_config(context=context)
            
            return client.ApiClient()
            
        except config.ConfigException as e:
            self.logger.error(f"Failed to load Kubernetes configuration: {e}")
            raise ValueError(f"Invalid Kubernetes configuration: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error initializing Kubernetes client: {e}")
            raise
    
    def _verify_connection(self) -> None:
        """
        Verifies the connection to the Kubernetes cluster by making a test API call.
        
        Raises:
            ConnectionError: If unable to connect to the cluster.
        """
        try:
            self.core_v1.list_namespace(limit=1)
            self.logger.info("Successfully connected to Kubernetes cluster")
        except ApiException as e:
            self.logger.error(f"Failed to connect to Kubernetes cluster: {e}")
            raise ConnectionError(f"Cannot connect to Kubernetes cluster: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error verifying connection: {e}")
            raise ConnectionError(f"Cannot verify Kubernetes connection: {e}")
    
    def get_id(self, resource_type: str, resource_block: Dict) -> Optional[str]:
        """
        Fetches the ID for a specific Kubernetes resource type and resource block.
        
        Args:
            resource_type (str): The type of the resource (e.g., 'kubernetes_deployment').
            resource_block (Dict): The resource configuration block.
            
        Returns:
            Optional[str]: Resource ID if found, or None if not found.
        """
        if resource_type in self._resources_dict:
            method = self._resources_dict[resource_type]
            return method(resource_block)
        else:
            self.logger.warning(f"Unsupported Kubernetes resource type: {resource_type}")
            return None
    
    def _extract_metadata(self, resource_block: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts name and namespace from resource metadata.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            tuple[Optional[str], Optional[str]]: Tuple of (name, namespace). Namespace defaults to 'default'.
        """
        try:
            after = resource_block.get('change', {}).get('after', {})
            if not after:
                # Try 'values' as fallback (used in some Terraform state formats)
                after = resource_block.get('values', {})
                if not after:
                    self.logger.debug("No 'after' or 'values' field found in resource block")
                    return None, 'default'
            
            metadata = after.get('metadata')
            if metadata is None:
                self.logger.debug("No 'metadata' field found in resource block")
                return None, 'default'
            
            # Handle both object and list formats
            if isinstance(metadata, list):
                # If metadata is a list, extract from items
                # Format: [{"name": "name", "value": "my-resource"}, {"name": "namespace", "value": "default"}]
                if not metadata:
                    self.logger.debug("Metadata list is empty")
                    return None, 'default'
                
                # Check if first item is a dict with direct metadata fields (not key-value pairs)
                if len(metadata) == 1 and isinstance(metadata[0], dict) and 'name' in metadata[0]:
                    # Format: [{"name": "my-resource", "namespace": "default"}]
                    return metadata[0].get('name'), metadata[0].get('namespace', 'default')
                
                # Otherwise, treat as key-value pair format
                name = None
                namespace = 'default'
                for item in metadata:
                    if isinstance(item, dict):
                        # Check if this is a key-value pair format
                        if item.get('name') == 'name':
                            name = item.get('value')
                        elif item.get('name') == 'namespace':
                            namespace = item.get('value', 'default')
                
                if name is None and metadata:
                    self.logger.debug(f"Metadata list has {len(metadata)} items but no 'name' field found")
                
                return name, namespace
            elif isinstance(metadata, dict):
                # If metadata is a dict, extract directly
                # Format: {"name": "my-resource", "namespace": "default"}
                name = metadata.get('name')
                namespace = metadata.get('namespace', 'default')
                
                # Handle empty metadata dict
                if not metadata:
                    self.logger.debug("Metadata dict is empty")
                    return None, 'default'
                
                # If name is still None, try nested structures
                if name is None:
                    # Check if there's a nested structure like metadata[0].name
                    if len(metadata) == 1 and isinstance(list(metadata.values())[0], dict):
                        nested = list(metadata.values())[0]
                        name = nested.get('name')
                        namespace = nested.get('namespace', 'default')
                    # Check if metadata has other keys that might indicate a different structure
                    elif metadata:
                        self.logger.debug(f"Metadata dict has keys but no 'name': {list(metadata.keys())}")
                
                return name, namespace
            else:
                self.logger.debug(f"Metadata is neither list nor dict: {type(metadata)}")
                return None, 'default'
        except Exception as e:
            self.logger.warning(f"Error extracting metadata: {e}")
            return None, 'default'
    
    def kubernetes_namespace(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes namespace identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Namespace name if found, otherwise None.
        """
        try:
            namespace_name, _ = self._extract_metadata(resource_block)
            
            if not namespace_name:
                self.logger.warning("Missing 'name' in namespace metadata")
                return None
            
            # Verify namespace exists
            try:
                self.core_v1.read_namespace(name=namespace_name)
                return namespace_name
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Namespace '{namespace_name}' not found")
                else:
                    self.logger.warning(f"Error retrieving namespace '{namespace_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving namespace: {e}")
        
        return None
    
    def kubernetes_pod(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes pod identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Pod identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            pod_name, namespace = self._extract_metadata(resource_block)
            
            if not pod_name:
                self.logger.warning("Missing 'name' in pod metadata")
                return None
            
            # Verify pod exists
            try:
                self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
                return f"{namespace}/{pod_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Pod '{pod_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving pod '{pod_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving pod: {e}")
        
        return None
    
    def kubernetes_deployment(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes deployment identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Deployment identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            deployment_name, namespace = self._extract_metadata(resource_block)
            
            if not deployment_name:
                self.logger.warning("Missing 'name' in deployment metadata")
                return None
            
            # Verify deployment exists
            try:
                self.apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
                return f"{namespace}/{deployment_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Deployment '{deployment_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving deployment '{deployment_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving deployment: {e}")
        
        return None
    
    def kubernetes_service(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes service identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Service identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            service_name, namespace = self._extract_metadata(resource_block)
            
            if not service_name:
                self.logger.warning("Missing 'name' in service metadata")
                return None
            
            # Verify service exists
            try:
                self.core_v1.read_namespaced_service(name=service_name, namespace=namespace)
                return f"{namespace}/{service_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Service '{service_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving service '{service_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving service: {e}")
        
        return None
    
    def kubernetes_config_map(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes ConfigMap identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: ConfigMap identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            config_map_name, namespace = self._extract_metadata(resource_block)
            
            if not config_map_name:
                self.logger.warning("Missing 'name' in ConfigMap metadata")
                return None
            
            # Verify ConfigMap exists
            try:
                self.core_v1.read_namespaced_config_map(name=config_map_name, namespace=namespace)
                return f"{namespace}/{config_map_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"ConfigMap '{config_map_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving ConfigMap '{config_map_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving ConfigMap: {e}")
        
        return None
    
    def kubernetes_secret(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes Secret identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Secret identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            secret_name, namespace = self._extract_metadata(resource_block)
            
            if not secret_name:
                self.logger.warning("Missing 'name' in Secret metadata")
                return None
            
            # Verify Secret exists
            try:
                self.core_v1.read_namespaced_secret(name=secret_name, namespace=namespace)
                return f"{namespace}/{secret_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Secret '{secret_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving Secret '{secret_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving Secret: {e}")
        
        return None
    
    def kubernetes_persistent_volume_claim(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes PersistentVolumeClaim identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: PVC identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            pvc_name, namespace = self._extract_metadata(resource_block)
            
            if not pvc_name:
                self.logger.warning("Missing 'name' in PersistentVolumeClaim metadata")
                return None
            
            # Verify PVC exists
            try:
                self.core_v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
                return f"{namespace}/{pvc_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"PersistentVolumeClaim '{pvc_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving PersistentVolumeClaim '{pvc_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving PersistentVolumeClaim: {e}")
        
        return None
    
    def kubernetes_stateful_set(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes StatefulSet identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: StatefulSet identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            stateful_set_name, namespace = self._extract_metadata(resource_block)
            
            if not stateful_set_name:
                self.logger.warning("Missing 'name' in StatefulSet metadata")
                return None
            
            # Verify StatefulSet exists
            try:
                self.apps_v1.read_namespaced_stateful_set(name=stateful_set_name, namespace=namespace)
                return f"{namespace}/{stateful_set_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"StatefulSet '{stateful_set_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving StatefulSet '{stateful_set_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving StatefulSet: {e}")
        
        return None
    
    def kubernetes_daemon_set(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes DaemonSet identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: DaemonSet identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            daemon_set_name, namespace = self._extract_metadata(resource_block)
            
            if not daemon_set_name:
                self.logger.warning("Missing 'name' in DaemonSet metadata")
                return None
            
            # Verify DaemonSet exists
            try:
                self.apps_v1.read_namespaced_daemon_set(name=daemon_set_name, namespace=namespace)
                return f"{namespace}/{daemon_set_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"DaemonSet '{daemon_set_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving DaemonSet '{daemon_set_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving DaemonSet: {e}")
        
        return None
    
    def kubernetes_ingress(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes Ingress identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Ingress identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            ingress_name, namespace = self._extract_metadata(resource_block)
            
            if not ingress_name:
                self.logger.warning("Missing 'name' in Ingress metadata")
                return None
            
            # Verify Ingress exists
            try:
                self.networking_v1.read_namespaced_ingress(name=ingress_name, namespace=namespace)
                return f"{namespace}/{ingress_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Ingress '{ingress_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving Ingress '{ingress_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving Ingress: {e}")
        
        return None
    
    def kubernetes_service_account(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes ServiceAccount identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: ServiceAccount identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            service_account_name, namespace = self._extract_metadata(resource_block)
            
            if not service_account_name:
                self.logger.warning("Missing 'name' in ServiceAccount metadata")
                return None
            
            # Verify ServiceAccount exists
            try:
                self.core_v1.read_namespaced_service_account(name=service_account_name, namespace=namespace)
                return f"{namespace}/{service_account_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"ServiceAccount '{service_account_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving ServiceAccount '{service_account_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving ServiceAccount: {e}")
        
        return None
    
    def kubernetes_role(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes Role identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: Role identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            role_name, namespace = self._extract_metadata(resource_block)
            
            if not role_name:
                self.logger.warning("Missing 'name' in Role metadata")
                return None
            
            # Verify Role exists
            try:
                self.rbac_authorization_v1.read_namespaced_role(name=role_name, namespace=namespace)
                return f"{namespace}/{role_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"Role '{role_name}' not found in namespace '{namespace}'")
                else:
                    self.logger.warning(f"Error retrieving Role '{role_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving Role: {e}")
        
        return None
    
    def kubernetes_role_binding(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes RoleBinding identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: RoleBinding identifier in format 'namespace/name' if found, otherwise None.
        """
        try:
            role_binding_name, namespace = self._extract_metadata(resource_block)
            
            if not role_binding_name:
                self.logger.warning("Missing 'name' in RoleBinding metadata")
                self.logger.debug(f"Resource block structure: {resource_block}")
                return None
            
            self.logger.debug(f"Looking for RoleBinding '{role_binding_name}' in namespace '{namespace}'")
            
            # Verify RoleBinding exists
            try:
                self.rbac_authorization_v1.read_namespaced_role_binding(name=role_binding_name, namespace=namespace)
                self.logger.info(f"Found RoleBinding '{role_binding_name}' in namespace '{namespace}'")
                return f"{namespace}/{role_binding_name}"
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"RoleBinding '{role_binding_name}' not found in namespace '{namespace}'")
                    # Try to list RoleBindings in the namespace to help debug
                    try:
                        role_bindings = self.rbac_authorization_v1.list_namespaced_role_binding(namespace=namespace)
                        existing_names = [rb.metadata.name for rb in role_bindings.items]
                        self.logger.debug(f"Existing RoleBindings in namespace '{namespace}': {existing_names}")
                        if role_binding_name in existing_names:
                            self.logger.warning(f"RoleBinding name found in list but read failed - possible permissions issue")
                    except Exception as list_error:
                        self.logger.debug(f"Could not list RoleBindings for debugging: {list_error}")
                else:
                    self.logger.warning(f"Error retrieving RoleBinding '{role_binding_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
            self.logger.debug(f"Resource block structure: {resource_block}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving RoleBinding: {e}")
            self.logger.debug(f"Resource block structure: {resource_block}", exc_info=True)
        
        return None
    
    def kubernetes_cluster_role(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes ClusterRole identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: ClusterRole name if found, otherwise None.
        """
        try:
            cluster_role_name, _ = self._extract_metadata(resource_block)
            
            if not cluster_role_name:
                self.logger.warning("Missing 'name' in ClusterRole metadata")
                return None
            
            # Verify ClusterRole exists
            try:
                self.rbac_authorization_v1.read_cluster_role(name=cluster_role_name)
                return cluster_role_name
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"ClusterRole '{cluster_role_name}' not found")
                else:
                    self.logger.warning(f"Error retrieving ClusterRole '{cluster_role_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving ClusterRole: {e}")
        
        return None
    
    def kubernetes_cluster_role_binding(self, resource_block: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the Kubernetes ClusterRoleBinding identifier.
        
        Args:
            resource_block (Dict[str, Any]): The resource block from Terraform.
            
        Returns:
            Optional[str]: ClusterRoleBinding name if found, otherwise None.
        """
        try:
            cluster_role_binding_name, _ = self._extract_metadata(resource_block)
            
            if not cluster_role_binding_name:
                self.logger.warning("Missing 'name' in ClusterRoleBinding metadata")
                return None
            
            # Verify ClusterRoleBinding exists
            try:
                self.rbac_authorization_v1.read_cluster_role_binding(name=cluster_role_binding_name)
                return cluster_role_binding_name
            except ApiException as e:
                if e.status == 404:
                    self.logger.warning(f"ClusterRoleBinding '{cluster_role_binding_name}' not found")
                else:
                    self.logger.warning(f"Error retrieving ClusterRoleBinding '{cluster_role_binding_name}': {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving ClusterRoleBinding: {e}")
        
        return None
