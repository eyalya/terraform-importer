import json
import subprocess
import os
import logging
from typing import List, Optional, Dict, Union, Tuple

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")


class TerraformHandler:
    """
    Utility class for executing Terraform commands.

    This class provides methods to interact with Terraform by running commands like
    `plan`, `show`, and `apply`. It supports operations like generating Terraform plans,
    analyzing them for changes, and applying configurations if necessary.

    Attributes:
        __base_commands (List[str]): Base Terraform command (`terraform`).
        __options (List[str]): Additional command-line options for Terraform.
        __terraform_folder (Optional[str]): Path to the Terraform configuration folder.
    """

    def __init__(self, terraform_folder: Optional[str] = None, options: Optional[List[str]] = None):
        """
        Initializes the TerraformHandler with the Terraform configuration folder and options.

        Args:
            terraform_folder (Optional[str]): Path to the Terraform folder. Defaults to None.
            options (Optional[List[str]]): Additional options for Terraform commands. Defaults to [].

        Raises:
            ValueError: If the specified Terraform folder does not exist.
        """
        self.__base_commands = ["terraform"]
        self.__options = options or []
        self.__terraform_folder = terraform_folder

        # Ensure the folder exists
        if self.__terraform_folder and not os.path.isdir(self.__terraform_folder):
            global_logger.error(f"Error: The folder '{self.__terraform_folder}' does not exist.")
            raise ValueError(f"The folder '{self.__terraform_folder}' does not exist.")

    def get_terraform_folder(self) -> Optional[str]:
        """
        Returns the Terraform configuration folder path.

        Returns:
            Optional[str]: Path to the Terraform folder.
        """
        return self.__terraform_folder

    def run_terraform_command(self, command: List[str]) -> Union[Tuple[str, str, int], None]:
        """
        Runs a Terraform command and returns the output, error, and return code.

        Args:
            command (List[str]): List of command parts to execute (e.g., ['terraform', 'plan']).

        Returns:
            Union[Tuple[str, str, int], None]: Tuple containing (stdout, stderr, return_code),
            or None in case of an exception.
        """
        try:
            original_cwd = os.getcwd()
            if self.__terraform_folder:
                os.chdir(self.__terraform_folder)

            global_logger.info(f"Executing command: {' '.join(command)}")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # global_logger.info(f"Command output:\n{result.stdout}")
            if result.stderr:
                global_logger.error(f"Command errors:\n{result.stderr}")

            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            global_logger.error(f"An error occurred while running command '{' '.join(command)}': {e}")
            return None
        finally:
            # Restore the original working directory
            os.chdir(original_cwd)

    def check_for_imports_only(self, log_stream: str) -> bool:
        """
        Checks if the log stream contains only import actions.

        Args:
            log_stream (str): A string containing the JSON log stream.

        Returns:
            bool: True if non-import actions are detected, False otherwise.
        """
        try:
            lines = log_stream.strip().splitlines()
            for line in lines:
                try:
                    log_entry = json.loads(line)
                    message = log_entry.get("@message", "")
                    if message.startswith("Plan"):
                        changes = log_entry.get("changes", {})
                        if changes.get("add", 0) > 0 or changes.get("change", 0) > 0 or changes.get("remove", 0) > 0:
                            global_logger.info(f"Non-import actions detected: {changes}")
                            return True
                except json.JSONDecodeError:
                    global_logger.warning(f"Invalid JSON entry in log: {line}")
                    continue

            global_logger.info("Only import actions detected in the plan.")
            return False
        except Exception as e:
            global_logger.error(f"Error while checking for imports: {e}")
            return True

    def apply_if_only_import(self, targets: List[str]) -> None:
        """
        Runs `terraform apply` if the plan contains only import actions.

        Args:
            targets (List[str]): List of Terraform resource targets to check and apply.
        """
        try:
            plan_command = self.__base_commands + ["plan", "-json"] + self.__options + targets
            stdout, _, _ = self.run_terraform_command(plan_command)

            if self.check_for_imports_only(stdout):
                global_logger.info("Plan contains non-import actions. Skipping apply.")
                return

            global_logger.info("Only import actions detected. Running `terraform apply`...")
            apply_command = self.__base_commands + ["apply"] + self.__options + targets
            stdout, stderr, return_code = self.run_terraform_command(apply_command)

            if return_code == 0:
                global_logger.info("Terraform apply completed successfully.")
            else:
                global_logger.error(f"Terraform apply failed:\n{stderr}")
        except Exception as e:
            global_logger.error(f"Error during apply operation: {e}")

    def run_terraform_plan(self, targets: List[str]) -> None:
        """
        Runs the `terraform plan` command.

        Args:
            targets (List[str]): List of Terraform resource targets.
        """
        try:
            plan_command = self.__base_commands + ["plan", "-out=plan.out"] + self.__options + targets
            stdout, stderr, return_code = self.run_terraform_command(plan_command)

            if return_code == 0:
                global_logger.info("Terraform plan executed successfully.")
            else:
                global_logger.error("Terraform plan failed.")
        except Exception as e:
            global_logger.error(f"Error during plan operation: {e}")

    def run_terraform_show(self, file_path: Optional[str] = None) -> Optional[Dict]:
        """
        Runs `terraform show -json` and optionally saves the output to a file.

        Args:
            file_path (Optional[str]): Path to save the JSON output.

        Returns:
            Optional[Dict]: Parsed JSON output from `terraform show`.
        """
        try:
            show_command = self.__base_commands + ["show", "-json", "plan.out"]
            stdout, stderr, return_code = self.run_terraform_command(show_command) ## terraform show doesnt handle "targets"

            if return_code == 0:
                json_data = json.loads(stdout)
                if file_path:
                    self.save_json_plan(json_data, file_path)
                return json_data
            else:
                global_logger.error("Terraform show failed.")
                global_logger.error(stderr)
        except Exception as e:
            global_logger.error(f"Error during `terraform show`: {e}")
        return None

    def save_json_plan(self, json_data: Dict, file_path: str) -> None:
        """
        Saves the JSON data to a file.

        Args:
            json_data (Dict): JSON data to save.
            file_path (str): Path to save the file.
        """
        try:
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)
            global_logger.info(f"Terraform plan JSON saved to {file_path}")
        except Exception as e:
            global_logger.error(f"Failed to save Terraform plan JSON: {e}")
