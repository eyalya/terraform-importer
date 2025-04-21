from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore.exceptions
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class GENERALService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.sqs_client = self.get_client("sqs")
        self.sns_client = self.get_client("sns")
        self.acm_client = self.get_client("acm")
        self.cloudfront_client = self.get_client("cloudfront")
        self.codebuild_client = self.get_client("codebuild")
        self._resources = [
            "aws_ecr_repository",
            "aws_sqs_queue",
            "aws_sns_topic",
            "aws_route53_record",
            "aws_acm_certificate",
            "aws_elastic_beanstalk_application",
            "aws_elasticache_cluster",
            "aws_elasticache_subnet_group",
            "aws_codebuild_project",
            "aws_cloudfront_distribution",
            "aws_codebuild_source_credential"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()


    #def aws_ecr_repository(self, resource):
    #    return resource['change']['after']['name']

    def aws_ecr_repository(self, resource):
    """
    Validates if the AWS ECR repository exists and returns its name.

    Args:
        resource (dict): The Terraform resource block.

    Returns:
        str: The ECR repository name if it exists, otherwise None.
    """
    try:
        # Extract repository name
        repository_name = resource['change']['after'].get('name')

        if not repository_name:
            global_logger.error("ECR repository name is missing in the resource data.")
            return None

        # Check if the repository exists
        response = self.ecr_client.describe_repositories(repositoryNames=[repository_name])

        # If the repository exists, return its name
        if response.get('repositories'):
            return repository_name

        global_logger.error(f"ECR repository '{repository_name}' not found.")
        return None

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            global_logger.error(f"ECR repository '{repository_name}' does not exist.")
        else:
            global_logger.error(f"AWS ClientError while validating ECR repository: {e}")
    except botocore.exceptions.BotoCoreError as e:
        global_logger.error(f"AWS BotoCoreError: {e}")
    except KeyError as e:
        global_logger.error(f"Missing key in resource data: {e}")
    except Exception as e:
        global_logger.error(f"Unexpected error occurred: {e}")

    return None

    #def aws_sqs_queue(self, resource):
    #    name = resource['change']['after']['name']
    #    try:
    #        # Get the queue URL
    #        response = self.sqs_client.get_queue_url(QueueName=name)
    #        return response['QueueUrl']
    #    except self.sqs_client.exceptions.QueueDoesNotExist:
    #        global_logger.INFO(f"The SQS queue '{name}' does not exist.")
    #        return None
    #    except Exception as e:
    #        global_logger.error(f"An error occurred: {e}")
    #        return None

    def aws_sqs_queue(self, resource):
        """
        Validates if the AWS SQS queue exists and returns its URL.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The SQS queue URL if it exists, otherwise None.
        """
        try:
            # Extract queue name
            name = resource['change']['after'].get('name')
    
            if not name:
                global_logger.error("SQS queue name is missing in the resource data.")
                return None
    
            # Check if the queue exists
            response = self.sqs_client.get_queue_url(QueueName=name)
            queue_url = response.get('QueueUrl')
    
            if queue_url:
                return queue_url
    
            global_logger.error(f"SQS queue '{name}' not found.")
            return None
    
        except self.sqs_client.exceptions.QueueDoesNotExist:
            global_logger.info(f"The SQS queue '{name}' does not exist.")
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating SQS queue: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    
    #def aws_sns_topic(self, resource):
    #    name = resource['change']['after']['name']
    #    try:
    #        # List all SNS topics
    #        paginator = self.sns_client.get_paginator('list_topics')
    #        for page in paginator.paginate():
    #            for topic in page['Topics']:
    #                topic_arn = topic['TopicArn']
    #                # Extract the topic name from the ARN
    #                if name == topic_arn.split(':')[-1]:
    #                    return topic_arn
    #
    #        global_logger.error(f"The SNS topic '{name}' does not exist.")
    #        return None
    #    except Exception as e:
    #        global_logger.error(f"An error occurred: {e}")
    #        return None

    def aws_sns_topic(self, resource):
        """
        Validates if the AWS SNS topic exists and returns its ARN.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The SNS topic ARN if it exists, otherwise None.
        """
        try:
            # Extract topic name
            name = resource['change']['after'].get('name')
    
            if not name:
                global_logger.error("SNS topic name is missing in the resource data.")
                return None
    
            # List all SNS topics using pagination
            paginator = self.sns_client.get_paginator('list_topics')
            for page in paginator.paginate():
                for topic in page.get('Topics', []):
                    topic_arn = topic.get('TopicArn')
    
                    if not topic_arn:
                        continue  # Skip invalid entries
    
                    # Extract the topic name from the ARN and compare
                    if name == topic_arn.split(':')[-1]:
                        return topic_arn
    
            global_logger.error(f"The SNS topic '{name}' does not exist.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating SNS topic: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_route53_record(self, resource):
    #    zone_id = f"{resource['change']['after']['zone_id']}"
    #    name = f"{resource['change']['after']['name']}"
    #    type = f"{resource['change']['after']['type']}"
    #    return  f"{zone_id}_{name}_{type}"

    def aws_route53_record(self, resource):
        """
        Validates if the AWS Route 53 record exists and returns its identifier.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The Route 53 record identifier if it exists, otherwise None.
        """
        try:
            # Extract required values
            zone_id = resource['change']['after'].get('zone_id')
            name = resource['change']['after'].get('name')
            record_type = resource['change']['after'].get('type')
    
            if not all([zone_id, name, record_type]):
                global_logger.error("Missing required Route 53 record attributes in resource data.")
                return None
    
            # List all records in the hosted zone
            paginator = self.route53_client.get_paginator('list_resource_record_sets')
            for page in paginator.paginate(HostedZoneId=zone_id):
                for record in page.get('ResourceRecordSets', []):
                    if record.get('Name') == name and record.get('Type') == record_type:
                        return f"{zone_id}_{name}_{record_type}"
    
            global_logger.error(f"Route 53 record '{name}' of type '{record_type}' does not exist in zone '{zone_id}'.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating Route 53 record: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_acm_certificate(self,resource):  #TODO: need check
    #    domain_name = resource['change']['after']['domain_name']
    #    certificates = self.acm_client.list_certificates(CertificateStatuses=['ISSUED'])
#
    #    for cert in certificates['CertificateSummaryList']:
    #        if domain_name:
    #            if cert['DomainName'] == domain_name:
    #                return cert['CertificateArn']
    #        return None

    def aws_acm_certificate(self, resource):
        """
        Validates if the AWS ACM certificate exists and returns its ARN.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The ACM certificate ARN if it exists, otherwise None.
        """
        try:
            # Extract domain name
            domain_name = resource['change']['after'].get('domain_name')
            
            if not domain_name:
                global_logger.error("Missing required attribute: 'domain_name'.")
                return None
    
            # List ACM certificates
            paginator = self.acm_client.get_paginator('list_certificates')
            for page in paginator.paginate(CertificateStatuses=['ISSUED']):
                for cert in page.get('CertificateSummaryList', []):
                    if cert.get('DomainName') == domain_name:
                        return cert.get('CertificateArn')
    
            global_logger.error(f"ACM certificate for domain '{domain_name}' does not exist or is not issued.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating ACM certificate: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_elastic_beanstalk_application(self, resource):
    #    return resource['change']['after']['name']

    def aws_elastic_beanstalk_application(self, resource):
        """
        Validates if the AWS Elastic Beanstalk application exists and returns its name.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The Elastic Beanstalk application name if it exists, otherwise None.
        """
        try:
            # Extract application name
            app_name = resource['change']['after'].get('name')
    
            if not app_name:
                global_logger.error("Missing required attribute: 'name'.")
                return None
    
            # Describe applications to check if it exists
            response = self.elasticbeanstalk_client.describe_applications(ApplicationNames=[app_name])
    
            if response.get('Applications'):
                return app_name
    
            global_logger.error(f"Elastic Beanstalk application '{app_name}' does not exist.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating Elastic Beanstalk application: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_elasticache_cluster(self, resource):
    #    return resource['change']['after']['cluster_id']

    def aws_elasticache_cluster(self, resource):
        """
        Validates if the AWS ElastiCache cluster exists and returns its cluster ID.
     
        Args:
            resource (dict): The Terraform resource block.
     
        Returns:
            str: The ElastiCache cluster ID if it exists, otherwise None.
        """
        try:
            # Extract cluster ID
            cluster_id = resource['change']['after'].get('cluster_id')
     
            if not cluster_id:
                global_logger.error("Missing required attribute: 'cluster_id'.")
                return None
     
            # Describe ElastiCache clusters to check if the cluster exists
            response = self.elasticache_client.describe_cache_clusters(
                CacheClusterId=cluster_id,
                ShowCacheNodeInfo=False
            )
     
            if response.get('CacheClusters'):
                return cluster_id
     
            global_logger.error(f"ElastiCache cluster '{cluster_id}' does not exist.")
            return None
     
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating ElastiCache cluster: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
     
         return None

    #def aws_elasticache_subnet_group(self, resource):
    #    return resource['change']['after']['name']

    def aws_elasticache_subnet_group(self, resource):
        """
        Validates if the AWS ElastiCache Subnet Group exists and returns its name.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The ElastiCache Subnet Group name if it exists, otherwise None.
        """
        try:
            # Extract subnet group name
            subnet_group_name = resource['change']['after'].get('name')
    
            if not subnet_group_name:
                global_logger.error("Missing required attribute: 'name'.")
                return None
    
            # Describe subnet groups to check if the subnet group exists
            response = self.elasticache_client.describe_cache_subnet_groups(
                CacheSubnetGroupName=subnet_group_name
            )
    
            if response.get('CacheSubnetGroups'):
                return subnet_group_name
    
            global_logger.error(f"ElastiCache Subnet Group '{subnet_group_name}' does not exist.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating ElastiCache Subnet Group: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None
    
    #def aws_codebuild_project(self, resource):
    #    return resource['change']['after']['name']

    def aws_codebuild_project(self, resource):
        """
        Validates if the AWS CodeBuild project exists and returns its name.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The CodeBuild project name if it exists, otherwise None.
        """
        try:
            # Extract project name
            project_name = resource['change']['after'].get('name')
    
            if not project_name:
                global_logger.error("Missing required attribute: 'name'.")
                return None
    
            # Describe the CodeBuild project to check if it exists
            response = self.codebuild_client.batch_get_projects(
                names=[project_name]
            )
    
            if response.get('projects'):
                return project_name
    
            global_logger.error(f"CodeBuild project '{project_name}' does not exist.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating CodeBuild project: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_cloudfront_distribution(self, resource):
    #    
    #    aliases = resource['change']['after']['aliases']
#
    #    paginator = self.cloudfront_client.get_paginator('list_distributions')
    #    page_iterator = paginator.paginate()
    #    
    #    for page in page_iterator:
    #        distributions = page.get('DistributionList', {}).get('Items', [])
    #        for distribution in distributions:
    #            # Get the list of aliases for this distribution
    #            distribution_aliases = distribution['Aliases']['Items']
    #    
    #            # Check if all required aliases are present
    #            if all(alias in distribution_aliases for alias in aliases):
    #                return distribution['Id']
    #    return None

    def aws_cloudfront_distribution(self, resource):
        """
        Validates if the CloudFront distribution with the provided aliases exists
        and returns its ID.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The CloudFront distribution ID if it exists and has the required aliases,
                 otherwise None.
        """
        try:
            # Extract aliases from the resource
            aliases = resource['change']['after'].get('aliases')
    
            if not aliases:
                global_logger.error("No aliases provided in the resource.")
                return None
    
            # Use paginator to handle large number of distributions
            paginator = self.cloudfront_client.get_paginator('list_distributions')
            page_iterator = paginator.paginate()
    
            for page in page_iterator:
                distributions = page.get('DistributionList', {}).get('Items', [])
                for distribution in distributions:
                    # Get the list of aliases for this distribution
                    distribution_aliases = distribution['Aliases']['Items']
    
                    # Check if all required aliases are present
                    if all(alias in distribution_aliases for alias in aliases):
                        return distribution['Id']
    
            # If no matching distribution is found
            global_logger.error(f"CloudFront distribution with aliases {aliases} does not exist.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating CloudFront distribution: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_codebuild_source_credential(self,resource):
#
    #    auth_type   = resource['change']['after']['auth_type']
    #    server_type = resource['change']['after']['server_type']
#
    #    response = self.codebuild_client.list_source_credentials()
    #    for credential in response.get('sourceCredentialsInfos', []):
    #        if credential['authType'] == auth_type and credential['serverType'] == server_type:
    #            return credential['arn']
    #    return None

    def aws_codebuild_source_credential(self, resource):
        """
        Validates if the CodeBuild source credential with the provided auth_type
        and server_type exists and returns its ARN.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The ARN of the CodeBuild source credential if it exists,
                 otherwise None.
        """
        try:
            # Extract auth_type and server_type from the resource
            auth_type = resource['change']['after'].get('auth_type')
            server_type = resource['change']['after'].get('server_type')
    
            if not auth_type or not server_type:
                global_logger.error("Missing 'auth_type' or 'server_type' in the resource.")
                return None
    
            # Use the AWS CodeBuild client to list source credentials
            response = self.codebuild_client.list_source_credentials()
    
            # Validate if the required source credential exists
            for credential in response.get('sourceCredentialsInfos', []):
                if credential['authType'] == auth_type and credential['serverType'] == server_type:
                    return credential['arn']
    
            # Log if the credential doesn't exist
            global_logger.error(f"CodeBuild source credential with auth_type: {auth_type} and server_type: {server_type} does not exist.")
            return None
    
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"AWS ClientError while validating CodeBuild source credential: {e}")
        except botocore.exceptions.BotoCoreError as e:
            global_logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            global_logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error occurred: {e}")
    
        return None

    