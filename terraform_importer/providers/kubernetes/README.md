# Kubernetes Provider

The Kubernetes provider requires explicit configuration for `config_context` and `config_path` in your Terraform configuration. These values must be strings, not Terraform expressions or references.

**Important:** These configuration values should be set in your Terraform configuration files (e.g., in your `provider "kubernetes"` blocks), and the tool reads them from there.

## Configuration Requirements

### `config_context`

Must be explicitly set to a string value representing the Kubernetes context name, or `null` if using the default context.

**Examples:**
- `"arn:aws:eks:us-east-1:********:cluster/cluster-name"`
- `"my-k8s-context"`
- `null` (uses default context from kubeconfig)

### `config_path`

Must be explicitly set to a string value representing the path to your kubeconfig file, or `null` to use the default location (`~/.kube/config`).

**Examples:**
- `"/Users/username/.kube/config"`
- `"~/.kube/config"` (tilde will be expanded to home directory)
- `null` (uses default `~/.kube/config`)

## Example Configuration

Configure these values in your Terraform configuration file (e.g., `providers.tf` or `main.tf`):

```hcl
provider "kubernetes" {
  config_context = "arn:aws:eks:us-east-1:********:cluster/cluster-name"
  config_path    = "/Users/username/.kube/config"
}
```

The tool extracts these values from your Terraform configuration and uses them to initialize the Kubernetes provider. The extracted configuration will look like:

```json
{
  "kubernetes": {
    "name": "kubernetes",
    "full_name": "registry.terraform.io/hashicorp/kubernetes",
    "expressions": {
      "config_context": "arn:aws:eks:us-east-1:********:cluster/cluster-name",
      "config_path": "/Users/username/.kube/config"
    }
  }
}
```

## Important Notes

- **Configuration Location:** These values must be set in your Terraform configuration files (not in a separate config file). The tool reads them from your Terraform provider blocks.
- **Do not use Terraform expressions or references** for `config_context` or `config_path`. These must be literal string values (e.g., `"arn:aws:eks:..."` not `module.eks.cluster_arn`).
- If invalid values are provided (e.g., Terraform references that couldn't be resolved), the provider initialization will fail with a warning, and the tool will continue without the Kubernetes provider.
- The tool will log warnings if it detects invalid configuration types and attempt to use default values where possible.
