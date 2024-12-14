import json
import subprocess
import os
import logging

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class TerraformHandler:
    """Utility class for executing Terraform commands."""
    
    def __init__(self, terraform_folder = None, options=[]):
        self.__base_commands = ["terraform"]
        self.__options = options
        self.__terraform_folder = terraform_folder

         # Ensure the folder exists
        if self.__terraform_folder and not os.path.isdir(self.__terraform_folder):
            global_logger.error(f"Error: The folder '{self.__terraform_folder}' does not exist.")
            raise ValueError

    def get_terraform_folder(self):
        return self.__terraform_folder
    
    def run_terraform_command(self, command):
        """
        Runs a Terraform command and returns the output, error, and return code.

        :param command: List of command parts to execute (e.g., ['terraform', 'plan', ...]).
        :return: Tuple (stdout, stderr, return_code)
        """
        try:
            original_cwd = os.getcwd()
            os.chdir(self.__terraform_folder)
            # delete_file_if_exists(file_path)
            # Run the `terraform plan` command
            # global_logger.info(f"Running 'terraform command' in '{self.__terraform_folder}'...")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            global_logger.error(f"An error occurred: {e}")
        finally:
            # Restore the original working directory
            os.chdir(original_cwd)
        return result.stdout, result.stderr, result.returncode

    def check_for_imports_only(self, log_stream):
        """
        Check For Imports Only, checking if the @message field starts with 'Plan'
        and determining if non-import actions are present.

        :param log_stream: A string containing the JSON log stream.
        :return: Boolean indicating whether non-import actions exist.
        """
        try:
            lines = log_stream.strip().splitlines()
            for line in lines:
                try:
                    log_entry = json.loads(line)
                    message = log_entry.get("@message", "")
                    # Check if the message starts with "Plan"
                    if message.startswith("Plan"):
                        # Extract changes summary
                        changes = log_entry.get("changes", {})
                        add = changes.get("add", 0)
                        change = changes.get("change", 0)
                        remove = changes.get("remove", 0)
                        import_count = changes.get("import", 0)
                        # Check for any action other than import
                        if add > 0 or change > 0 or remove > 0:
                            global_logger.info(f"Non-import actions detected: {changes}")
                            return True
                except json.JSONDecodeError:
                    global_logger.info(f"Invalid JSON line: {line}")
                    continue

            global_logger.info("Only import actions detected.")
            return False
        except Exception as e:
            global_logger.info(f"An error occurred: {e}")
            return True

    def apply_if_only_import(self, targets):
        """
        Runs `terraform plan` with a list of targets and checks if only imports are present.
        If only imports are detected, it calls `terraform apply` for those imports.
        :param targets: List of Terraform resource targets.
        """
        try:
            
            plan_command = self.__base_commands + ["plan", "-json"] + self.__options + targets
            
            stdout, stderr, return_code = self.run_terraform_command(plan_command)
            has_non_import_actions = self.process_terraform_logs(stdout)
            
            if has_non_import_actions:
                global_logger.info("Plan contains non-import operations. Skipping apply.")
            else:
                global_logger.info("Only import operations detected. Running Terraform apply for imports...")
                apply_command = self.__base_commands + ["apply"] + self.__options + targets
                stdout, stderr, return_code = self.run_terraform_command(apply_command)

                if return_code == 0:
                    global_logger.info("Terraform apply completed successfully.")
                else:
                    global_logger.info(f"Terraform apply failed:\n{stderr}")
        except Exception as e:
            global_logger.info(f"An error occurred: {e}")
    
    def run_terraform_plan(self, targets):
        """
        Runs the `terraform plan` command for the specified Terraform folder.
        
        :param terraform_folder: Path to the folder containing Terraform configurations.
        """
        plan_command = self.__base_commands + ["plan", "-out=plan.out"] + self.__options + targets
            
        stdout, stderr, return_code = self.run_terraform_command(plan_command)
        
        # Output the result
        if return_code == 0:
            global_logger.info("Terraform plan executed successfully. Output:")
            global_logger.info(stdout)
        else:
            global_logger.info("Terraform plan failed. Error:")
            global_logger.info(stderr)
    
    def run_terraform_show(self, file_path=None):
        """
        Runs the `terraform show -json` command for the specified Terraform folder
        and saves the output to a file.

        :param terraform_folder: Path to the folder containing Terraform configurations.
        :param output_file: Path to the file where the JSON output will be saved.
        """
        plan_command = self.__base_commands + ["show", "-json", f"plan.out"] + self.__options
            
        stdout, stderr, return_code = self.run_terraform_command(plan_command)
        
        # Output the result
        if return_code == 0:
            global_logger.info("Terraform show executed successfully. Output:")
            json_data = json.loads(stdout)
            if file_path:
                self.save_json_plan(json_data, file_path)
            return json_data
        else:
            global_logger.error("Terraform show failed. Error:")
            global_logger.error(stderr)
            return None
    
    def save_json_plan(self, json_data, file_path):
        """
        """
        try:
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
            global_logger.info(f"Terraform show output saved to '{file_path}' a json file")
        except Exception as e:
            global_logger.error(f"Terraform show output failed to save as json")