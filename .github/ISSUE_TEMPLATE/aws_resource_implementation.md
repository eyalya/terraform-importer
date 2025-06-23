---
name: AWS Resource Implementation
about: Template for adding support for new AWS resources
title: '[AWS Resource] Add support for {resource_type}'
labels: enhancement, aws-resource, good first issue
assignees: ''
---

## Resource Type
AWS Resource Type: `aws_{service}_{resource}` (e.g., `aws_s3_bucket`, `aws_iam_role`)

## Implementation Steps

### 1. Terraform State Analysis
First, analyze the Terraform state structure for this resource type:
1. Create a sample resource in your AWS account
2. Add it to a Terraform configuration
3. Run `terraform show` to understand the state structure
4. Document the key identifiers and attributes needed for importing

Example state structure:
```hcl
# Example terraform show output for this resource type
resource "aws_example_resource" "sample" {
    id             = "resource-id"
    name           = "resource-name"
    # Document other important attributes
}
```

Key fields needed for import:
- Primary identifier: (e.g., bucket name for S3, role ARN for IAM)
- Required attributes for matching
- Naming patterns

### 2. AWS API Analysis
Document the AWS API calls needed to:
1. List all resources of this type
2. Get specific resource details
3. Match Terraform state attributes with AWS API response

Example API flow:
```python
# Document the AWS API calls needed
client.list_resources()  # Lists all resources
client.describe_resource()  # Gets detailed information
```

### 3. Resource Handler Implementation
Create a new class in the appropriate service module:
```python
from terraform_importer.providers.aws.base import AWSResourceHandler

class {ResourceType}Handler(AWSResourceHandler):
    def __init__(self):
        super().__init__()
        self.client = self.get_client("{aws_service}")   # e.g., "s3", "iam"
        self.resources= ["aws_{service}_{resource}", ...]

    def list_resources(self):
        try:
            client = self.get_client()
            
            # 1. Get list of resources from AWS
            resources = []
            try:
                response = client.list_{resources}()
                # Handle pagination if needed
                
                for item in response['{items_key}']:
                    # 2. For each resource, get the details needed to match Terraform state
                    details = client.describe_{resource}(...)
                    
                    # 3. Extract the identifier that matches Terraform's expected format
                    resource_id = self._format_resource_id(details)
                    
                    # 4. Add to resources list if valid
                    if resource_id:
                        resources.append({
                            'id': resource_id,
                            'type': self.resource_type,
                            'name': self._generate_resource_name(details)
                        })
                    
            except client.exceptions.ClientError as e:
                self.logger.error(f"AWS API error: {e}")
                return []
                
            return resources
            
        except Exception as e:
            self.logger.error(f"Unexpected error during resource discovery: {e}")
            return []

    def _format_resource_id(self, details):
        """Convert AWS API response to Terraform resource ID format"""
        try:
            # Transform AWS resource identifier into Terraform expected format
            # Document the transformation logic
            return formatted_id
        except Exception as e:
            self.logger.warning(f"Could not format resource ID: {e}")
            return None

    def _generate_resource_name(self, details):
        """Generate a valid Terraform resource name from AWS details"""
        try:
            # Create a valid Terraform resource name
            return valid_name
        except Exception as e:
            self.logger.warning(f"Could not generate resource name: {e}")
            return "resource"
```

### 4. Testing Requirements
- Create a real resource in AWS for testing
- Document its Terraform configuration
- Add unit tests with mocked AWS API responses
- Test the resource ID formatting
- Test name generation
- Test error handling
- Verify import block generation matches Terraform's expectations

### 5. Documentation
- Document the AWS API calls used
- Document the ID format transformation
- Document any limitations or special cases
- Add examples of supported resource configurations

## Testing Checklist
- [ ] Terraform state structure analyzed and documented
- [ ] AWS API calls identified and documented
- [ ] Resource handler implemented
- [ ] ID formatting logic tested
- [ ] Resource name generation tested
- [ ] Error handling implemented and tested
- [ ] Import block generation verified with real resources
- [ ] Documentation updated

## Additional Notes
- All new class function must use "try" and "except" to prevent system break.
- Always test with real AWS resources first to understand the state structure
- Verify the import works with different resource configurations
- Consider edge cases in resource naming and ID formats
- Document any assumptions about AWS API responses

## Resources
- [AWS SDK Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Show Command Documentation](https://www.terraform.io/docs/cli/commands/show.html) 