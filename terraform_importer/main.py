from terraform_importer.manager import Manager
from terraform_importer.cli import TerraformImporterCLI
import logging

def main():

    cli = TerraformImporterCLI()
    args = cli.parse_args()

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    # Extract arguments
    terraform_config_path = args.config
    # Split each option string by spaces to create an array of individual options
    options = []
    for option_string in args.option:
        options.extend(option_string.split())
    targets = args.target

    logging.debug(f"Config path: {terraform_config_path}")
    logging.debug(f"Options: {options}")
    logging.debug(f"Targets: {targets}")

    # Run the manager
    manager = Manager(terraform_config_path, options, targets)
    manager.run()

if __name__ == "__main__":
    main()
