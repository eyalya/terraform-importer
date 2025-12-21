import argparse
import os
import sys

class AppendOptionAction(argparse.Action):
    """
    Custom action to handle --option values that may start with '-'.
    
    This allows both:
    - --option '-var-file=prod.tfvars' (quoted, standard way)
    - --option=-var-file=prod.tfvars (equals format, standard way)
    - --option -var-file=prod.tfvars (space-separated, convenience)
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)
    
    def __call__(self, parser, namespace, values, option_string=None):
        # Initialize the list if it doesn't exist
        if not hasattr(namespace, self.dest):
            setattr(namespace, self.dest, [])
        
        # Append the value
        getattr(namespace, self.dest).append(values)

class TerraformImporterCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Run Terraform Importer.")
        self._add_arguments()
    
    def _preprocess_args(self, args):
        """
        Preprocess arguments to handle --option values starting with '-'.
        
        This is a convenience feature to support --option -value format.
        The conventional ways (quoted or equals format) work without preprocessing.
        """
        # Known long options that should not be treated as values for --option
        known_options = {'--config', '--target', '--log-level', '--option', '--help', '-h'}
        
        processed = []
        i = 0
        while i < len(args):
            if args[i] == '--option' and i + 1 < len(args):
                next_arg = args[i + 1]
                # If next arg starts with '-' but is not a known long option, combine them
                # This handles cases like: --option -var-file=prod.tfvars
                if next_arg.startswith('-') and next_arg not in known_options:
                    # Combine: --option -value becomes --option=-value
                    processed.append(f"--option={next_arg}")
                    i += 2
                else:
                    # Normal case: --option value or --option=value
                    processed.append(args[i])
                    i += 1
            else:
                processed.append(args[i])
                i += 1
        return processed

    def _add_arguments(self):
        # Required: path to config
        self.parser.add_argument(
            "--config", required=True,
            help="Path to Terraform configuration directory"
        )

        # Optional: repeated options
        # Using custom action to handle values starting with '-'
        # Standard formats: --option '-var-file=prod.tfvars' or --option=-var-file=prod.tfvars
        # Also supports: --option -var-file=prod.tfvars (convenience, via preprocessing)
        self.parser.add_argument(
            "--option", action=AppendOptionAction, default=[],
            metavar="VALUE",
            help="Optional flags or arguments to terraform command (can be repeated). "
                 "Standard formats: --option '-var-file=prod.tfvars' or --option=-var-file=prod.tfvars. "
                 "Also supports: --option -var-file=prod.tfvars"
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

    def parse_args(self, args=None):
        # Preprocess arguments to handle --option -value format
        if args is None:
            args = sys.argv[1:]
        processed_args = self._preprocess_args(args)
        parsed_args = self.parser.parse_args(processed_args)

        # Validate config path early
        if not os.path.isdir(parsed_args.config):
            print(f"Error: '{parsed_args.config}' is not a valid directory.")
            sys.exit(1)

        return parsed_args

