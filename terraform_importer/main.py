from terraform_importer.manager import Manager
from terraform_importer.providers import AWSProvider, GCPProvider
import logging

def main():

    


    providers = [AWSProvider(), GCPProvider()]
    terraform_config_path = "path/to/terraform/configs"
    output_path = "path/to/output/file"
    
    manager = Manager(providers, terraform_config_path, output_path)
    manager.run()

if __name__ == "__main__":
    main()
