import unittest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock kubernetes module before importing the provider
mock_kubernetes = MagicMock()
mock_client = MagicMock()
mock_config = MagicMock()

# Create a mock ApiException class
class MockApiException(Exception):
    def __init__(self, status=404, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status

# Set up mock client classes
mock_api_client_instance = MagicMock()
mock_core_v1_class = MagicMock()
mock_apps_v1_class = MagicMock()
mock_networking_v1_class = MagicMock()
mock_rbac_class = MagicMock()
mock_storage_class = MagicMock()

mock_client.ApiClient = lambda: mock_api_client_instance
mock_client.CoreV1Api = lambda api_client: MagicMock()
mock_client.AppsV1Api = lambda api_client: MagicMock()
mock_client.NetworkingV1Api = lambda api_client: MagicMock()
mock_client.RbacAuthorizationV1Api = lambda api_client: MagicMock()
mock_client.StorageV1Api = lambda api_client: MagicMock()

mock_rest = MagicMock()
mock_rest.ApiException = MockApiException
mock_client.rest = mock_rest

mock_kubernetes.client = mock_client
mock_kubernetes.config = mock_config
mock_config.load_kube_config = MagicMock()
mock_config.load_incluster_config = MagicMock()

sys.modules['kubernetes'] = mock_kubernetes
sys.modules['kubernetes.client'] = mock_client
sys.modules['kubernetes.config'] = mock_config
sys.modules['kubernetes.client.rest'] = mock_rest

from terraform_importer.providers.kubernetes.kubernetes_provider import KubernetesProvider

# Use the mock ApiException for tests
ApiException = MockApiException


class TestKubernetesProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up class-level patches"""
        cls.patcher_config = patch('terraform_importer.providers.kubernetes.kubernetes_provider.config.load_kube_config')
        cls.patcher_api_client = patch('terraform_importer.providers.kubernetes.kubernetes_provider.client.ApiClient')
        cls.patcher_core_v1 = patch('terraform_importer.providers.kubernetes.kubernetes_provider.client.CoreV1Api')
        cls.patcher_apps_v1 = patch('terraform_importer.providers.kubernetes.kubernetes_provider.client.AppsV1Api')
        cls.patcher_networking_v1 = patch('terraform_importer.providers.kubernetes.kubernetes_provider.client.NetworkingV1Api')
        cls.patcher_rbac = patch('terraform_importer.providers.kubernetes.kubernetes_provider.client.RbacAuthorizationV1Api')
        cls.patcher_storage = patch('terraform_importer.providers.kubernetes.kubernetes_provider.client.StorageV1Api')
        
        cls.patcher_config.start()
        cls.patcher_api_client.start()
        cls.patcher_core_v1.start()
        cls.patcher_apps_v1.start()
        cls.patcher_networking_v1.start()
        cls.patcher_rbac.start()
        cls.patcher_storage.start()
    
    @classmethod
    def tearDownClass(cls):
        """Stop class-level patches"""
        cls.patcher_config.stop()
        cls.patcher_api_client.stop()
        cls.patcher_core_v1.stop()
        cls.patcher_apps_v1.stop()
        cls.patcher_networking_v1.stop()
        cls.patcher_rbac.stop()
        cls.patcher_storage.stop()
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_auth_config = {
            "expressions": {
                "config_path": None,
                "context": None,
                "in_cluster": False
            }
        }
        
        # Mock API clients
        self.mock_core_v1 = MagicMock()
        self.mock_apps_v1 = MagicMock()
        self.mock_networking_v1 = MagicMock()
        self.mock_rbac_authorization_v1 = MagicMock()
        self.mock_storage_v1 = MagicMock()
        self.mock_api_client = MagicMock()
        
        # Mock successful connection verification
        self.mock_core_v1.list_namespace.return_value = MagicMock()
        
        # Set return values for the patched classes
        from terraform_importer.providers.kubernetes import kubernetes_provider
        kubernetes_provider.client.ApiClient = lambda: self.mock_api_client
        kubernetes_provider.client.CoreV1Api = lambda api_client: self.mock_core_v1
        kubernetes_provider.client.AppsV1Api = lambda api_client: self.mock_apps_v1
        kubernetes_provider.client.NetworkingV1Api = lambda api_client: self.mock_networking_v1
        kubernetes_provider.client.RbacAuthorizationV1Api = lambda api_client: self.mock_rbac_authorization_v1
        kubernetes_provider.client.StorageV1Api = lambda api_client: self.mock_storage_v1
        
        # Create provider instance
        self.provider = KubernetesProvider(self.mock_auth_config)
        
        # Ensure clients are our mocks
        self.provider.core_v1 = self.mock_core_v1
        self.provider.apps_v1 = self.mock_apps_v1
        self.provider.networking_v1 = self.mock_networking_v1
        self.provider.rbac_authorization_v1 = self.mock_rbac_authorization_v1
        self.provider.storage_v1 = self.mock_storage_v1

    def test_init(self):
        """Test KubernetesProvider initialization"""
        self.assertEqual(self.provider.__name__, "kubernetes")
        self.assertIsNotNone(self.provider.core_v1)
        self.assertIsNotNone(self.provider.apps_v1)

    def test_get_id_unsupported_resource(self):
        """Test get_id with unsupported resource type"""
        result = self.provider.get_id("kubernetes_unsupported", {})
        self.assertIsNone(result)

    def test_kubernetes_namespace_success(self):
        """Test kubernetes_namespace with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-namespace"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespace.return_value = MagicMock()
        
        result = self.provider.kubernetes_namespace(resource)
        
        self.assertEqual(result, "test-namespace")
        self.mock_core_v1.read_namespace.assert_called_once_with(name="test-namespace")

    def test_kubernetes_namespace_not_found(self):
        """Test kubernetes_namespace when namespace doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-namespace"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespace.side_effect = api_exception
        
        result = self.provider.kubernetes_namespace(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_namespace_missing_name(self):
        """Test kubernetes_namespace with missing name"""
        resource = {
            "change": {
                "after": {
                    "metadata": {}
                }
            }
        }
        
        result = self.provider.kubernetes_namespace(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_pod_success(self):
        """Test kubernetes_pod with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-pod",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_pod.return_value = MagicMock()
        
        result = self.provider.kubernetes_pod(resource)
        
        self.assertEqual(result, "default/test-pod")
        self.mock_core_v1.read_namespaced_pod.assert_called_once_with(name="test-pod", namespace="default")

    def test_kubernetes_pod_not_found(self):
        """Test kubernetes_pod when pod doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-pod",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespaced_pod.side_effect = api_exception
        
        result = self.provider.kubernetes_pod(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_pod_default_namespace(self):
        """Test kubernetes_pod with default namespace"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-pod"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_pod.return_value = MagicMock()
        
        result = self.provider.kubernetes_pod(resource)
        
        self.assertEqual(result, "default/test-pod")
        self.mock_core_v1.read_namespaced_pod.assert_called_once_with(name="test-pod", namespace="default")

    def test_kubernetes_deployment_success(self):
        """Test kubernetes_deployment with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-deployment",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_apps_v1.read_namespaced_deployment.return_value = MagicMock()
        
        result = self.provider.kubernetes_deployment(resource)
        
        self.assertEqual(result, "default/test-deployment")
        self.mock_apps_v1.read_namespaced_deployment.assert_called_once_with(name="test-deployment", namespace="default")

    def test_kubernetes_deployment_not_found(self):
        """Test kubernetes_deployment when deployment doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-deployment",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_apps_v1.read_namespaced_deployment.side_effect = api_exception
        
        result = self.provider.kubernetes_deployment(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_service_success(self):
        """Test kubernetes_service with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-service",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_service.return_value = MagicMock()
        
        result = self.provider.kubernetes_service(resource)
        
        self.assertEqual(result, "default/test-service")
        self.mock_core_v1.read_namespaced_service.assert_called_once_with(name="test-service", namespace="default")

    def test_kubernetes_service_not_found(self):
        """Test kubernetes_service when service doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-service",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespaced_service.side_effect = api_exception
        
        result = self.provider.kubernetes_service(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_config_map_success(self):
        """Test kubernetes_config_map with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-configmap",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_config_map.return_value = MagicMock()
        
        result = self.provider.kubernetes_config_map(resource)
        
        self.assertEqual(result, "default/test-configmap")
        self.mock_core_v1.read_namespaced_config_map.assert_called_once_with(name="test-configmap", namespace="default")

    def test_kubernetes_config_map_not_found(self):
        """Test kubernetes_config_map when configmap doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-configmap",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespaced_config_map.side_effect = api_exception
        
        result = self.provider.kubernetes_config_map(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_secret_success(self):
        """Test kubernetes_secret with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-secret",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_secret.return_value = MagicMock()
        
        result = self.provider.kubernetes_secret(resource)
        
        self.assertEqual(result, "default/test-secret")
        self.mock_core_v1.read_namespaced_secret.assert_called_once_with(name="test-secret", namespace="default")

    def test_kubernetes_secret_not_found(self):
        """Test kubernetes_secret when secret doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-secret",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespaced_secret.side_effect = api_exception
        
        result = self.provider.kubernetes_secret(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_persistent_volume_claim_success(self):
        """Test kubernetes_persistent_volume_claim with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-pvc",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_persistent_volume_claim.return_value = MagicMock()
        
        result = self.provider.kubernetes_persistent_volume_claim(resource)
        
        self.assertEqual(result, "default/test-pvc")
        self.mock_core_v1.read_namespaced_persistent_volume_claim.assert_called_once_with(name="test-pvc", namespace="default")

    def test_kubernetes_persistent_volume_claim_not_found(self):
        """Test kubernetes_persistent_volume_claim when PVC doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-pvc",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespaced_persistent_volume_claim.side_effect = api_exception
        
        result = self.provider.kubernetes_persistent_volume_claim(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_stateful_set_success(self):
        """Test kubernetes_stateful_set with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-statefulset",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_apps_v1.read_namespaced_stateful_set.return_value = MagicMock()
        
        result = self.provider.kubernetes_stateful_set(resource)
        
        self.assertEqual(result, "default/test-statefulset")
        self.mock_apps_v1.read_namespaced_stateful_set.assert_called_once_with(name="test-statefulset", namespace="default")

    def test_kubernetes_stateful_set_not_found(self):
        """Test kubernetes_stateful_set when statefulset doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-statefulset",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_apps_v1.read_namespaced_stateful_set.side_effect = api_exception
        
        result = self.provider.kubernetes_stateful_set(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_daemon_set_success(self):
        """Test kubernetes_daemon_set with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-daemonset",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_apps_v1.read_namespaced_daemon_set.return_value = MagicMock()
        
        result = self.provider.kubernetes_daemon_set(resource)
        
        self.assertEqual(result, "default/test-daemonset")
        self.mock_apps_v1.read_namespaced_daemon_set.assert_called_once_with(name="test-daemonset", namespace="default")

    def test_kubernetes_daemon_set_not_found(self):
        """Test kubernetes_daemon_set when daemonset doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-daemonset",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_apps_v1.read_namespaced_daemon_set.side_effect = api_exception
        
        result = self.provider.kubernetes_daemon_set(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_ingress_success(self):
        """Test kubernetes_ingress with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-ingress",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_networking_v1.read_namespaced_ingress.return_value = MagicMock()
        
        result = self.provider.kubernetes_ingress(resource)
        
        self.assertEqual(result, "default/test-ingress")
        self.mock_networking_v1.read_namespaced_ingress.assert_called_once_with(name="test-ingress", namespace="default")

    def test_kubernetes_ingress_not_found(self):
        """Test kubernetes_ingress when ingress doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-ingress",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_networking_v1.read_namespaced_ingress.side_effect = api_exception
        
        result = self.provider.kubernetes_ingress(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_service_account_success(self):
        """Test kubernetes_service_account with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-sa",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_core_v1.read_namespaced_service_account.return_value = MagicMock()
        
        result = self.provider.kubernetes_service_account(resource)
        
        self.assertEqual(result, "default/test-sa")
        self.mock_core_v1.read_namespaced_service_account.assert_called_once_with(name="test-sa", namespace="default")

    def test_kubernetes_service_account_not_found(self):
        """Test kubernetes_service_account when service account doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-sa",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_core_v1.read_namespaced_service_account.side_effect = api_exception
        
        result = self.provider.kubernetes_service_account(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_role_success(self):
        """Test kubernetes_role with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-role",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_rbac_authorization_v1.read_namespaced_role.return_value = MagicMock()
        
        result = self.provider.kubernetes_role(resource)
        
        self.assertEqual(result, "default/test-role")
        self.mock_rbac_authorization_v1.read_namespaced_role.assert_called_once_with(name="test-role", namespace="default")

    def test_kubernetes_role_not_found(self):
        """Test kubernetes_role when role doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-role",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_rbac_authorization_v1.read_namespaced_role.side_effect = api_exception
        
        result = self.provider.kubernetes_role(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_role_binding_success(self):
        """Test kubernetes_role_binding with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-rolebinding",
                        "namespace": "default"
                    }
                }
            }
        }
        self.mock_rbac_authorization_v1.read_namespaced_role_binding.return_value = MagicMock()
        
        result = self.provider.kubernetes_role_binding(resource)
        
        self.assertEqual(result, "default/test-rolebinding")
        self.mock_rbac_authorization_v1.read_namespaced_role_binding.assert_called_once_with(name="test-rolebinding", namespace="default")

    def test_kubernetes_role_binding_not_found(self):
        """Test kubernetes_role_binding when role binding doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-rolebinding",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_rbac_authorization_v1.read_namespaced_role_binding.side_effect = api_exception
        
        result = self.provider.kubernetes_role_binding(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_cluster_role_success(self):
        """Test kubernetes_cluster_role with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-clusterrole"
                    }
                }
            }
        }
        self.mock_rbac_authorization_v1.read_cluster_role.return_value = MagicMock()
        
        result = self.provider.kubernetes_cluster_role(resource)
        
        self.assertEqual(result, "test-clusterrole")
        self.mock_rbac_authorization_v1.read_cluster_role.assert_called_once_with(name="test-clusterrole")

    def test_kubernetes_cluster_role_not_found(self):
        """Test kubernetes_cluster_role when cluster role doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-clusterrole"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_rbac_authorization_v1.read_cluster_role.side_effect = api_exception
        
        result = self.provider.kubernetes_cluster_role(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_cluster_role_binding_success(self):
        """Test kubernetes_cluster_role_binding with successful response"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-clusterrolebinding"
                    }
                }
            }
        }
        self.mock_rbac_authorization_v1.read_cluster_role_binding.return_value = MagicMock()
        
        result = self.provider.kubernetes_cluster_role_binding(resource)
        
        self.assertEqual(result, "test-clusterrolebinding")
        self.mock_rbac_authorization_v1.read_cluster_role_binding.assert_called_once_with(name="test-clusterrolebinding")

    def test_kubernetes_cluster_role_binding_not_found(self):
        """Test kubernetes_cluster_role_binding when cluster role binding doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-clusterrolebinding"
                    }
                }
            }
        }
        api_exception = ApiException(status=404)
        self.mock_rbac_authorization_v1.read_cluster_role_binding.side_effect = api_exception
        
        result = self.provider.kubernetes_cluster_role_binding(resource)
        
        self.assertIsNone(result)

    def test_extract_metadata_dict_format(self):
        """Test _extract_metadata with dict format"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-resource",
                        "namespace": "test-ns"
                    }
                }
            }
        }
        
        name, namespace = self.provider._extract_metadata(resource)
        
        self.assertEqual(name, "test-resource")
        self.assertEqual(namespace, "test-ns")

    def test_extract_metadata_list_format(self):
        """Test _extract_metadata with list format"""
        resource = {
            "change": {
                "after": {
                    "metadata": [
                        {"name": "name", "value": "test-resource"},
                        {"name": "namespace", "value": "test-ns"}
                    ]
                }
            }
        }
        
        name, namespace = self.provider._extract_metadata(resource)
        
        self.assertEqual(name, "test-resource")
        self.assertEqual(namespace, "test-ns")

    def test_extract_metadata_default_namespace(self):
        """Test _extract_metadata with default namespace"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-resource"
                    }
                }
            }
        }
        
        name, namespace = self.provider._extract_metadata(resource)
        
        self.assertEqual(name, "test-resource")
        self.assertEqual(namespace, "default")

    def test_extract_metadata_invalid_format(self):
        """Test _extract_metadata with invalid format"""
        resource = {
            "change": {
                "after": {
                    "metadata": "invalid"
                }
            }
        }
        
        name, namespace = self.provider._extract_metadata(resource)
        
        self.assertIsNone(name)
        self.assertEqual(namespace, "default")

    def test_kubernetes_pod_api_error_non_404(self):
        """Test kubernetes_pod with non-404 API error"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-pod",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=500)
        self.mock_core_v1.read_namespaced_pod.side_effect = api_exception
        
        result = self.provider.kubernetes_pod(resource)
        
        self.assertIsNone(result)

    def test_kubernetes_deployment_api_error_non_404(self):
        """Test kubernetes_deployment with non-404 API error"""
        resource = {
            "change": {
                "after": {
                    "metadata": {
                        "name": "test-deployment",
                        "namespace": "default"
                    }
                }
            }
        }
        api_exception = ApiException(status=403)
        self.mock_apps_v1.read_namespaced_deployment.side_effect = api_exception
        
        result = self.provider.kubernetes_deployment(resource)
        
        self.assertIsNone(result)
    

if __name__ == "__main__":
    unittest.main()
