---
name: AWS Resource Support Expansion
about: Roadmap for implementing additional AWS resource types
title: '[Roadmap] AWS Resource Support Expansion'
labels: enhancement, roadmap, aws-resource
assignees: ''
---

# AWS Resource Support Expansion

This is our primary roadmap issue for expanding AWS resource support in the Terraform Importer tool. Each resource type will be implemented following our [AWS Resource Implementation Guidelines](link-to-guidelines).

## Priority Resource Types

### Phase 1 - Core Infrastructure
- [ ] AWS VPC Resources
  - [ ] aws_vpc
  - [ ] aws_subnet
  - [ ] aws_internet_gateway
  - [ ] aws_route_table
  - [ ] aws_security_group

- [ ] AWS EC2 Resources
  - [ ] aws_instance
  - [ ] aws_ebs_volume
  - [ ] aws_launch_template
  - [ ] aws_key_pair

- [ ] AWS S3 Resources
  - [ ] aws_s3_bucket
  - [ ] aws_s3_bucket_policy
  - [ ] aws_s3_bucket_versioning

### Phase 2 - Identity and Access
- [ ] AWS IAM Resources
  - [ ] aws_iam_role
  - [ ] aws_iam_policy
  - [ ] aws_iam_user
  - [ ] aws_iam_group

### Phase 3 - Database and Storage
- [ ] AWS RDS Resources
  - [ ] aws_db_instance
  - [ ] aws_db_subnet_group
  - [ ] aws_db_parameter_group

- [ ] AWS DynamoDB Resources
  - [ ] aws_dynamodb_table
  - [ ] aws_dynamodb_global_table

### Phase 4 - Application Services
- [ ] AWS Lambda Resources
  - [ ] aws_lambda_function
  - [ ] aws_lambda_permission
  - [ ] aws_lambda_layer_version

- [ ] AWS API Gateway Resources
  - [ ] aws_api_gateway_rest_api
  - [ ] aws_api_gateway_resource
  - [ ] aws_api_gateway_method

## Implementation Guidelines

Each resource implementation should:
1. Follow the error handling patterns established in the codebase
2. Include comprehensive logging
3. Handle AWS API pagination where applicable
4. Include unit tests with mocked AWS responses
5. Include integration tests (optional but recommended)
6. Update documentation

## Resource Implementation Process

1. Pick a resource from the list above
2. Create a new issue using the AWS Resource Implementation template
3. Follow the implementation guidelines
4. Submit a PR with the implementation
5. Update this roadmap issue when complete

## Progress Tracking

- Total Resources Planned: X
- Resources Implemented: Y
- Current Phase: 1
- Next Review Date: YYYY-MM-DD

## Additional Notes

- Priority may shift based on community needs
- New resource types may be added to this list
- Each resource implementation should be its own PR
- Community contributions are welcome!

## Related Links
- [AWS Resource Implementation Template](link-to-template)
- [Contributing Guidelines](link-to-contributing)
- [AWS SDK Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 