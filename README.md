# Terraform Import Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
A Python-based tool for analyzing Terraform configurations and generating resource import blocks dynamically. This tool helps DevOps engineers and infrastructure teams to easily import existing cloud resources into their Terraform state.

## Features
- Detection of existing cloud resources that are missing from Terraform state (due to state loss)
- Prevention of resource recreation by automatically generating import blocks
- Reconciliation of actual cloud infrastructure with Terraform configurations
- Support for multiple cloud providers
- Easy-to-use command-line interface
- Customizable import configurations

### Key Benefits
- Prevents accidental resource recreation when Terraform state is lost or out of sync
- Helps recover from state file losses without manual intervention
- Reduces the risk of disruption to production environments

## Installation

### Prerequisites
- Python 3.7 or higher
- Terraform 0.12 or higher
- AWS CLI (for AWS resources)

### Using pip
```bash
pip install -r requirements.txt
```

### From source
```bash
git clone https://github.com/eyalya/terraform-importer.git
cd terraform-importer
pip install -e .
```

## Quick Start

### Prerequisites
- Python 3.7 or higher
- Terraform 0.12 or higher
- Valid cloud provider authentication configured on your machine
- Terraform configuration files in a directory

### Installation
1. Install the package:
   ```bash
   pip3 install -r requirements.txt
   pip3 install -e .
   ```

### Usage
1. Ensure you have valid cloud provider credentials configured (e.g., AWS credentials in `~/.aws/credentials` or environment variables)

2. Run the tool by pointing it to your Terraform configuration directory. You can use either method:

   Using the command-line tool (recommended):
   ```bash
   terraform-importer --config /path/to/terraform/config
   ```

   Or using the Python module directly:
   ```bash
   python3 -m terraform_importer.main --config /path/to/terraform/config
   ```

### Additional Options
- `--target`: Specify specific resource addresses to import
- `--option`: Pass additional options to the Terraform command
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Example with options:
```bash
terraform-importer \
  --config /path/to/terraform/config \
  --target aws_s3_bucket.my_bucket \
  --log-level DEBUG
```

## Usage Examples

### Basic Usage
```bash
# Import resources from a Terraform configuration directory
terraform-importer --config /path/to/terraform/config

# Import specific resources using the target flag
terraform-importer --config /path/to/terraform/config --target aws_s3_bucket.my_bucket

# Run with debug logging
terraform-importer --config /path/to/terraform/config --log-level DEBUG
```

### Advanced Configuration
For advanced usage and configuration options, see our [detailed documentation](docs/advanced-usage.md).

## Project Structure
- `terraform_importer/`: Main package containing the core logic
- `tests/`: Unit tests and integration tests
- `docs/`: Detailed documentation
- `examples/`: Example configurations and use cases

## Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to:
- Submit issues
- Submit pull requests
- Development setup
- Coding standards

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support
- Create an issue for bug reports or feature requests
- Join our [Discord community](link-to-discord) for discussions
- Check out our [FAQ](docs/faq.md)

## Acknowledgments
- Thanks to all contributors who have helped shape this project
- Special thanks to the Terraform community

## Roadmap
- [ ] Complete support for AWS resources (expanding supported resource types)
- [ ] Support for Azure resources
- [ ] Support for GCP resources
- [ ] Interactive mode
- [ ] Resource dependency detection
- [ ] State file analysis

