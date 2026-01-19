"""
Integration tests for KubernetesProvider - requires real cluster connection.

Run with:
    python -m terraform_importer.providers.kubernetes.tests.test_kubernetes_integration
"""
import unittest
from terraform_importer.providers.kubernetes.kubernetes_provider import KubernetesProvider


class TestKubernetesIntegration(unittest.TestCase):
    """Integration tests that connect to a real Kubernetes cluster."""

    def test_real_cluster_connection(self):
        """Integration test to verify real connection to EKS cluster."""
        provider = KubernetesProvider({
            "expressions": {
                "config_context": "arn:aws:eks:us-east-1:173115710334:cluster/eco-plant-cluster",
                "config_path": "/Users/eyal_ya/.kube/config"
            }
        })

        # Use core_v1 API to list namespaces
        namespaces = provider.core_v1.list_namespace()
        

        print(f"\nFound {len(namespaces.items)} namespaces:")
        for ns in namespaces.items:
            print(f"  - {ns.metadata.name}")

        # Assert we got at least one namespace (kube-system should always exist)
        self.assertGreater(len(namespaces.items), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
