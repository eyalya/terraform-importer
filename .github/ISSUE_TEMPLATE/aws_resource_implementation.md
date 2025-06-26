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

### 3. Resource Implementation
- name of function should be the name of the resource (e.g aws_autoscaling_group )
- function should have two steps:
1. create id
2. verify resource exist
- add function name to list of resources of the module (self._resources)
- resource should handle exception and follow our code convention


### 4. Testing Requirements
- Test on a real resource
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