from manager import Manager
from terraform_importer.providers.aws_provider import AWSProvider
import logging

def main():

    providers = [AWSProvider()]
    terraform_config_path = "path/to/terraform/configs"
    output_path = "path/to/output/file"
    options = []
    targets=[]
    
    manager = Manager(providers, terraform_config_path, output_path, options, targets)
    manager.run()

if __name__ == "__main__":
    main()
