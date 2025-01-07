from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
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


    def aws_ecr_repository(self, resource):
        return resource['change']['after']['name']

    def aws_sqs_queue(self, resource):
        name = resource['change']['after']['name']
        try:
            # Get the queue URL
            response = self.sqs_client.get_queue_url(QueueName=name)
            return response['QueueUrl']
        except self.sqs_client.exceptions.QueueDoesNotExist:
            global_logger.INFO(f"The SQS queue '{name}' does not exist.")
            return None
        except Exception as e:
            global_logger.error(f"An error occurred: {e}")
            return None

    
    def aws_sns_topic(self, resource):
        name = resource['change']['after']['name']
        try:
            # List all SNS topics
            paginator = self.sns_client.get_paginator('list_topics')
            for page in paginator.paginate():
                for topic in page['Topics']:
                    topic_arn = topic['TopicArn']
                    # Extract the topic name from the ARN
                    if name == topic_arn.split(':')[-1]:
                        return topic_arn
    
            global_logger.error(f"The SNS topic '{name}' does not exist.")
            return None
        except Exception as e:
            global_logger.error(f"An error occurred: {e}")
            return None

    def aws_route53_record(self, resource):
        zone_id = f"{resource['change']['after']['zone_id']}"
        name = f"{resource['change']['after']['name']}"
        type = f"{resource['change']['after']['type']}"
        return  f"{zone_id}_{name}_{type}"

    def aws_acm_certificate(self,resource):  #TODO: need check
        domain_name = resource['change']['after']['domain_name']
        certificates = self.acm_client.list_certificates(CertificateStatuses=['ISSUED'])

        for cert in certificates['CertificateSummaryList']:
            if domain_name:
                if cert['DomainName'] == domain_name:
                    return cert['CertificateArn']
            return None

    def aws_elastic_beanstalk_application(self, resource):
        return resource['change']['after']['name']

    def aws_elasticache_cluster(self, resource):
        return resource['change']['after']['cluster_id']

    def aws_elasticache_subnet_group(self, resource):
        return resource['change']['after']['name']
    
    def aws_codebuild_project(self, resource):
        return resource['change']['after']['name']

    def aws_cloudfront_distribution(self, resource):
        
        aliases = resource['change']['after']['aliases']

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
        return None

    def aws_codebuild_source_credential(self,resource):

        auth_type   = resource['change']['after']['auth_type']
        server_type = resource['change']['after']['server_type']

        response = self.codebuild_client.list_source_credentials()
        for credential in response.get('sourceCredentialsInfos', []):
            if credential['authType'] == auth_type and credential['serverType'] == server_type:
                return credential['arn']
        return None

    