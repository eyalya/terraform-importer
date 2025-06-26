import argparse
import os
import sys

class TerraformImporterCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Run Terraform Importer.")
        self._add_arguments()

    def _add_arguments(self):
        # Required: path to config
        self.parser.add_argument(
            "--config", required=True,
            help="Path to Terraform configuration directory"
        )

        # Optional: repeated options
        self.parser.add_argument(
            "--option", action="append", default=[],
            help="Optional flags or arguments to terraform command (can be repeated)"
        )

        # Optional: repeated targets
        self.parser.add_argument(
            "--target", action="append", default=[],
            help="Target resource addresses to import (can be repeated)"
        )

        # Optional: logging level
        self.parser.add_argument(
            "--log-level", default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set logging level (default: INFO)"
        )

    def parse_args(self):
        args = self.parser.parse_args()

        # Validate config path early
        if not os.path.isdir(args.config):
            print(f"Error: '{args.config}' is not a valid directory.")
            sys.exit(1)

        return args

