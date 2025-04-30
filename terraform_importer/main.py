from terraform_importer.manager import Manager
import logging
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Run Terraform Importer.")

    # Required: path to config
    parser.add_argument(
        "--config", required=True,
        help="Path to Terraform configuration directory"
    )

    # Optional: repeated options
    parser.add_argument(
        "--option", action="append", default=[],
        help="Optional flags or arguments to terraform command (can be repeated)"
    )

    # Optional: repeated targets
    parser.add_argument(
        "--target", action="append", default=[],
        help="Target resource addresses to import (can be repeated)"
    )

    # Optional: logging level
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Validate config path
    if not os.path.isdir(args.config):
        print(f"Error: '{args.config}' is not a valid directory.")
        sys.exit(1)

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Extract arguments
    terraform_config_path = args.config
    options = args.option
    targets = args.target

    logging.debug(f"Config path: {terraform_config_path}")
    logging.debug(f"Options: {options}")
    logging.debug(f"Targets: {targets}")

    # Run the manager
    manager = Manager(terraform_config_path, options, targets)
    manager.run()

if __name__ == "__main__":
    main()
