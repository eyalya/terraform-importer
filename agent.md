# Terraform Importer - AI Agent Guidelines

This document provides comprehensive guidelines for AI agents assisting with development, refactoring, and contributions to the Terraform Importer project.

## Project Context

Terraform Importer is a Python-based tool for:
- Detecting existing cloud resources missing from Terraform state
- Generating import blocks to prevent resource recreation
- Reconciling cloud infrastructure with Terraform configurations

## Core Principles

1. **Always read existing code** before proposing changes
2. **Follow existing patterns** in the codebase
3. **Tests are mandatory** for all new functionality
4. **Use appropriate log levels** as defined below
5. **Keep changes focused** - avoid scope creep

---

## Logging Conventions

### Log Level Guidelines

| Level | When to Use | Examples |
|-------|-------------|----------|
| **ERROR** | Actual system errors, unexpected exceptions | File I/O failures, network errors, critical config errors |
| **WARNING** | Provider-level issues (expected but notable) | Resource not found, provider unavailable, API rate limits |
| **INFO** | General operational information | Starting operations, successful finds, config loaded |
| **DEBUG** | Detailed troubleshooting data | API details, internal state, variable values |

### Examples

```python
# ERROR - Only for actual system failures
self.logger.error(f"Failed to write import blocks to file: {e}")
self.logger.error(f"Unexpected error in processing: {e}")

# WARNING - Provider/resource issues (expected scenarios)
self.logger.warning(f"Resource '{name}' not found in AWS")
self.logger.warning(f"Provider '{provider}' is not configured")
self.logger.warning(f"API rate limit exceeded, retrying...")
self.logger.warning(f"Missing optional field '{field}' in resource")

# INFO - Normal operational messages
self.logger.info(f"Processing resource type: {resource_type}")
self.logger.info(f"Successfully imported {count} resources")
self.logger.info(f"Configuration loaded from {path}")

# DEBUG - Detailed troubleshooting
self.logger.debug(f"API response: {response}")
self.logger.debug(f"Resource block contents: {resource}")
```

### Key Rule
**Resource not found, provider not exist, missing configuration = WARNING, not ERROR**

---

## Testing Requirements

### Mandatory Testing Policy
- **ALL** new services MUST have corresponding test files
- **ALL** new resource handlers MUST have unit tests
- **ALL** bug fixes SHOULD include regression tests

### Test File Locations

| Component | Test Location |
|-----------|---------------|
| AWS services | `terraform_importer/providers/aws/tests/test_<service>.py` |
| Other providers | `terraform_importer/providers/<provider>/tests/test_<module>.py` |
| Core modules | `tests/test_<module>.py` |

### Required Test Cases

For each resource handler, include tests for:
1. **Success case** - Resource exists and ID is returned
2. **Not found case** - Resource doesn't exist in cloud
3. **Missing data case** - Required fields missing from resource block
4. **Error handling** - API errors, exceptions

### Test Template

```python
import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.<service> import <Service>Service


class Test<Service>Service(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = <Service>Service(self.mock_session)

    def test_init(self):
        """Test service initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("<service_name>")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = ["aws_<resource_type>"]
        self.assertEqual(resources, expected_resources)

    def test_aws_<resource>_success(self):
        """Test aws_<resource> with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-resource"
                }
            }
        }
        self.mock_client.describe_<resources>.return_value = {
            "<Resources>": [{"<Resource>Id": "res-12345678"}]
        }
        
        result = self.service.aws_<resource>(resource)
        
        self.assertEqual(result, "res-12345678")

    def test_aws_<resource>_not_found(self):
        """Test aws_<resource> when resource doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-resource"
                }
            }
        }
        self.mock_client.describe_<resources>.return_value = {
            "<Resources>": []
        }
        
        result = self.service.aws_<resource>(resource)
        
        self.assertIsNone(result)

    def test_aws_<resource>_client_error(self):
        """Test aws_<resource> with ClientError"""
        resource = {
            "change": {
                "after": {
                    "name": "test-resource"
                }
            }
        }
        self.mock_client.describe_<resources>.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ResourceNotFound"}}, "Describe<Resources>"
        )
        
        result = self.service.aws_<resource>(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
```

### Running Tests

```bash
# Run all tests
python3 -m unittest tests

# Run specific test file
python3 -m unittest tests/test_specific.py

# Run provider-specific tests
python3 -m unittest terraform_importer.providers.aws.tests.test_<service>

# Run with verbose output
python3 -m unittest -v tests
```

---

## New Service Implementation Guide

### AWS Service Checklist

When implementing a new AWS service handler:

- [ ] Create service file: `terraform_importer/providers/aws/aws_services/<service>.py`
- [ ] Inherit from `BaseAWSService`
- [ ] Initialize logger: `self.logger = logging.getLogger(__name__)`
- [ ] Initialize client: `self.client = self.get_client("<service_name>")`
- [ ] Define `_resources` list
- [ ] Implement `get_resource_list()` method
- [ ] Implement resource handlers for each resource type
- [ ] Use correct log levels (WARNING for not found, ERROR for system errors)
- [ ] Create test file: `terraform_importer/providers/aws/tests/test_<service>.py`
- [ ] Add tests for all resource handlers
- [ ] Register service in provider

### Service Template

```python
from typing import List, Optional, Dict
import boto3
import botocore.exceptions
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService


class <Service>Service(BaseAWSService):
    """
    Handles <Service>-related resources.
    """
    
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.client = self.get_client("<service_name>")
        self._resources = [
            "aws_<resource_type_1>",
            "aws_<resource_type_2>",
        ]

    def get_resource_list(self) -> List[str]:
        """
        Returns the list of supported resource types.
        
        Returns:
            list: A copy of the resources list.
        """
        return self._resources.copy()
    
    def aws_<resource_type>(self, resource: Dict) -> Optional[str]:
        """
        Retrieves the AWS <Resource> ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            Optional[str]: The resource ID if it exists, otherwise None.
        """
        try:
            # Extract required values
            name = resource['change']['after'].get('name')
            
            if not name:
                self.logger.warning("Missing 'name' in resource data")
                return None
            
            # Query AWS to validate existence
            response = self.client.describe_<resources>(
                Names=[name]  # or appropriate filter
            )
            
            if response.get('<Resources>'):
                return response['<Resources>'][0]['<Resource>Id']
            
            self.logger.warning(f"<Resource> '{name}' not found in AWS")
            return None
            
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.warning(f"AWS ClientError: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.warning(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None
```

---

## Pull Request Guidelines

### Before Creating a PR

1. **Run all tests locally**
   ```bash
   python3 -m unittest tests
   ```

2. **Check for lint errors**

3. **Self-review your changes**

4. **Ensure proper log levels**

### PR Title Format
- Use present tense, imperative mood
- Be concise but descriptive
- Examples:
  - "Add support for aws_dynamodb_table resource"
  - "Fix resource ID extraction for ECS services"
  - "Update logging levels in EC2 service"

### PR Description Template

```markdown
## Description
Brief summary of changes and motivation.

Fixes #<issue_number>

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests that verify your changes.

- [ ] Unit tests for new resource handlers
- [ ] Integration tests (if applicable)
- [ ] Manual testing with real AWS resources

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I used appropriate log levels (WARNING for provider issues, ERROR only for system errors)
```

---

## Code Style Reference

### Imports Order
1. Standard library imports
2. Related third-party imports
3. Local application imports

```python
from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import logging

import boto3
import botocore.exceptions

from terraform_importer.providers.aws.aws_services.base import BaseAWSService
```

### Docstrings
Use Google-style docstrings:

```python
def method_name(self, param1: str, param2: Dict) -> Optional[str]:
    """
    Brief description of what the method does.
    
    Args:
        param1 (str): Description of param1.
        param2 (Dict): Description of param2.
    
    Returns:
        Optional[str]: Description of return value.
    
    Raises:
        ValueError: When invalid input is provided.
    """
```

### Error Handling Pattern

```python
try:
    # Main logic
    result = self.client.some_operation(...)
    
    if not result.get('Items'):
        self.logger.warning(f"Resource not found")  # WARNING, not ERROR
        return None
    
    return result['Items'][0]['Id']
    
except KeyError as e:
    self.logger.warning(f"Missing expected key: {e}")
except botocore.exceptions.ClientError as e:
    self.logger.warning(f"AWS ClientError: {e}")
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")  # Only unexpected = ERROR

return None
```

---

## Quick Reference

### File Locations
| File Type | Location |
|-----------|----------|
| AWS services | `terraform_importer/providers/aws/aws_services/` |
| AWS tests | `terraform_importer/providers/aws/tests/` |
| Base provider | `terraform_importer/providers/base_provider.py` |
| Core tests | `tests/` |

### Key Commands
```bash
# Run tests
python3 -m unittest tests

# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Contributing Files
- `CONTRIBUTING.md` - Full contributing guide
- `CODE_OF_CONDUCT.md` - Community guidelines
- `.github/pull_request_template.md` - PR template
- `.github/ISSUE_TEMPLATE/` - Issue templates
