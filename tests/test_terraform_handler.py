import unittest
import sys
import os
import json
import subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import  Mock, patch, MagicMock, mock_open
from terraform_importer.handlers.terraform_handler import TerraformHandler


class TestTerraformHandler(unittest.TestCase):

    def setUp(self):
        """
        This setup method will initialize a valid TerraformHandler and mock the file system.
        """
        self.patcher = patch("os.path.isdir")
        self.mock_isdir = self.patcher.start()
        self.mock_valid_folder = "/valid/terraform/folder"
        self.mock_invalid_folder = "/invalid/terraform/folder"

    def tearDown(self):
        """ Stop all patches. """
        self.patcher.stop()

    ####### __init__ #########

    def test_init_with_valid_folder(self):
        """ Test the constructor with a valid Terraform folder. """
        self.mock_isdir.return_value = True

        handler = TerraformHandler(terraform_folder=self.mock_valid_folder)

        self.assertEqual(handler.get_terraform_folder(), self.mock_valid_folder)
        self.mock_isdir.assert_called_once_with(self.mock_valid_folder)

    def test_init_with_invalid_folder(self):
        """ Test the constructor with an invalid Terraform folder. """
        self.mock_isdir.return_value = False
        
        with self.assertRaises(ValueError):
            TerraformHandler(terraform_folder=self.mock_invalid_folder)
        self.mock_isdir.assert_called_once_with(self.mock_invalid_folder)

    def test_init_with_no_folder(self):
        """ Test the constructor with no folder (None). """
        handler = TerraformHandler(terraform_folder=None)
        self.assertIsNone(handler.get_terraform_folder())
        self.mock_isdir.assert_not_called()

    def test_init_with_options(self):
        """ Test the constructor with additional options passed. """
        self.mock_isdir.return_value = True
        options = ["-var", "example=true"]
        
        handler = TerraformHandler(terraform_folder=self.mock_valid_folder, options=options)

        self.assertEqual(handler._TerraformHandler__options, options)

    ####### get_terraform_folder #########

    def test_get_terraform_folder_with_folder(self):
        """ Test get_terraform_folder when a folder is set. """
        self.mock_isdir.return_value = True
        handler = TerraformHandler(terraform_folder=self.mock_valid_folder)
        self.assertEqual(handler.get_terraform_folder(), self.mock_valid_folder)

    def test_get_terraform_folder_with_none(self):
        """ Test get_terraform_folder when the folder is None. """
        self.mock_isdir.return_value = True
        handler = TerraformHandler(terraform_folder=None)
        self.assertIsNone(handler.get_terraform_folder())

    ####### run_terraform_command #########

    @patch("subprocess.run")
    @patch("os.chdir")
    @patch("os.getcwd")
    def test_run_terraform_command_success(self, mock_getcwd, mock_chdir, mock_subprocess_run):
        """ Test running a Terraform command successfully. """
        mock_subprocess_run.return_value = MagicMock(stdout="Terraform plan output", stderr="", returncode=0)
        mock_getcwd.return_value = "/current/dir"

        handler = TerraformHandler(terraform_folder=self.mock_valid_folder)
        command = ["terraform", "plan"]

        stdout, stderr, returncode = handler.run_terraform_command(command)

        self.assertEqual(stdout, "Terraform plan output")
        self.assertEqual(stderr, "")
        self.assertEqual(returncode, 0)

        mock_chdir.assert_any_call(self.mock_valid_folder)
        mock_subprocess_run.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    @patch("subprocess.run")
    @patch("os.chdir")
    @patch("os.getcwd")
    def test_run_terraform_command_with_error(self, mock_getcwd, mock_chdir, mock_subprocess_run):
        """ Test running a Terraform command with an error. """
        mock_subprocess_run.return_value = MagicMock(stdout="", stderr="Error: something went wrong", returncode=1)
        mock_getcwd.return_value = "/current/dir"

        handler = TerraformHandler(terraform_folder=self.mock_valid_folder)
        command = ["terraform", "apply"]

        stdout, stderr, returncode = handler.run_terraform_command(command)

        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Error: something went wrong")
        self.assertEqual(returncode, 1)

        mock_chdir.assert_any_call(self.mock_valid_folder)
        mock_subprocess_run.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    @patch("subprocess.run")
    @patch("os.chdir")
    @patch("os.getcwd")
    def test_run_terraform_command_exception(self, mock_getcwd, mock_chdir, mock_subprocess_run):
        """ Test the case where an exception occurs during the Terraform command execution. """
        mock_subprocess_run.side_effect = Exception("An unexpected error occurred")
        mock_getcwd.return_value = "/current/dir"

        handler = TerraformHandler(terraform_folder=self.mock_valid_folder)
        command = ["terraform", "destroy"]

        result = handler.run_terraform_command(command)

        self.assertIsNone(result)

        mock_chdir.assert_any_call(self.mock_valid_folder)
        mock_subprocess_run.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    @patch("subprocess.run")
    @patch("os.chdir")
    @patch("os.getcwd")
    def test_run_terraform_command_no_folder(self, mock_getcwd, mock_chdir, mock_subprocess_run):
        """ Test running a Terraform command when no terraform folder is set. """
        mock_subprocess_run.return_value = MagicMock(stdout="Terraform plan output", stderr="", returncode=0)
        mock_getcwd.return_value = "/current/dir"

        handler = TerraformHandler(terraform_folder=None)  # No folder set
        command = ["terraform", "plan"]

        stdout, stderr, returncode = handler.run_terraform_command(command)

        self.assertEqual(stdout, "Terraform plan output")
        self.assertEqual(stderr, "")
        self.assertEqual(returncode, 0)

        mock_chdir.assert_called_once()
        mock_subprocess_run.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    ####### check_for_imports_only #########

    
    @patch('json.loads')
    @patch('terraform_importer.handlers.terraform_handler.global_logger')
    def test_check_for_imports_only(self, mock_global_logger, mock_json_loads):
        # Test case where the log stream contains only import actions
        log_stream = '{"@message": "Plan", "changes": {"add": 0, "change": 0, "remove": 0}}'
        mock_json_loads.return_value = {
            "@message": "Plan",
            "changes": {"add": 0, "change": 0, "remove": 0}
        }
        
        handler = TerraformHandler(self.mock_valid_folder) 
        result = handler.check_for_imports_only(log_stream)
        
        # Assert that the result is False because there are only import actions
        self.assertFalse(result)
        mock_global_logger.info.assert_called_with("Only import actions detected in the plan.")

        # Test case where the log stream contains non-import actions
        log_stream_non_import = '{"@message": "Plan", "changes": {"add": 1, "change": 0, "remove": 0}}'
        mock_json_loads.return_value = {
            "@message": "Plan",
            "changes": {"add": 1, "change": 0, "remove": 0}
        }

        result_non_import = handler.check_for_imports_only(log_stream_non_import)

        # Assert that the result is True because non-import actions are present
        self.assertTrue(result_non_import)
        mock_global_logger.info.assert_called()
 
    ####### apply_if_only_import #########

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.check_for_imports_only')  # Mock check_for_imports_only
    def test_apply_if_only_import(self, mock_check_for_imports_only, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for the case where the plan contains only import actions
        targets = ["target1", "target2"]
        plan_output = '{"@message": "Plan", "changes": {"add": 0, "change": 0, "remove": 0}}'
        mock_check_for_imports_only.return_value = False  # Simulating only import actions

        # Simulating the plan command output
        mock_run_terraform_command.side_effect = [
            (plan_output, "", 0),  # First call to run_terraform_command (for the plan command)
            ("", "apply error", 1)  # Second call to run_terraform_command (for the apply command)
        ]
        
        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder) 
        
        # Call the method
        result = handler.apply_if_only_import(targets)
        
        base_commands = handler._TerraformHandler__base_commands
        options = handler._TerraformHandler__options

        # Check that the plan command was executed with the expected arguments
        mock_run_terraform_command.assert_any_call(
            base_commands + ["plan", "-json"] + options + targets
        )
        
        # Check that check_for_imports_only was called with the plan output
        mock_check_for_imports_only.assert_called_with(plan_output)
        
        # Assert that info log for running apply was called
        mock_global_logger.info.assert_any_call("Only import actions detected. Running `terraform apply`...")
        
        # Check that the apply command was executed with the expected arguments
        mock_run_terraform_command.assert_any_call(
            base_commands + ["apply"] + options + targets
        )
        
        # Assert that the error log was called because the apply command failed
        mock_global_logger.error.assert_any_call("Terraform apply failed:\napply error")

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.check_for_imports_only')  # Mock check_for_imports_only
    def test_apply_if_only_import_non_import_plan(self, mock_check_for_imports_only, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for the case where the plan contains non-import actions
        targets = ["target1", "target2"]
        plan_output = '{"@message": "Plan", "changes": {"add": 1, "change": 0, "remove": 0}}'
        mock_check_for_imports_only.return_value = True  # Simulating non-import actions

        # Simulating the plan command output
        mock_run_terraform_command.side_effect = [
            (plan_output, "", 0),  # First call to run_terraform_command (for the plan command)
        ]
        
        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder) 
                
        # Call the method
        result = handler.apply_if_only_import(targets)
        
        base_commands = handler._TerraformHandler__base_commands
        options = handler._TerraformHandler__options

        # Check that the plan command was executed with the expected arguments
        mock_run_terraform_command.assert_any_call(
            base_commands + ["plan", "-json"] + options + targets
        )
        
        # Check that check_for_imports_only was called with the plan output
        mock_check_for_imports_only.assert_called_with(plan_output)
        
        # Assert that info log for skipping apply due to non-import actions was called
        mock_global_logger.info.assert_any_call("Plan contains non-import actions. Skipping apply.")
        
        # Ensure the apply command was not called
        with self.assertRaises(AssertionError):
           mock_run_terraform_command.assert_called_with(
            base_commands + ["apply"] + options + targets
           )
    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.check_for_imports_only')  # Mock check_for_imports_only
    def test_apply_if_only_import_exception(self, mock_check_for_imports_only, mock_run_terraform_command, mock_global_logger):
        # Test case where an exception occurs during apply operation
        targets = ["target1", "target2"]
        mock_check_for_imports_only.return_value = False
        mock_run_terraform_command.side_effect = Exception("Test exception")
        
        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder) 
                
        # Call the method
        result = handler.apply_if_only_import(targets)
        
        # Assert that the error log was called due to the exception
        mock_global_logger.error.assert_called_with("Error during apply operation: Test exception")

    ####### run_terraform_plan #########

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    def test_run_terraform_plan_success(self, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for successful plan execution
        targets = ["target1", "target2"]
        plan_output = "Terraform plan executed"
        mock_run_terraform_command.return_value = (plan_output, "", 0)  # Success return code

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method
        handler.run_terraform_plan(targets)
        
        base_commands = handler._TerraformHandler__base_commands
        options = handler._TerraformHandler__options

        # Check that the plan command was executed with the expected arguments
        mock_run_terraform_command.assert_called_once_with(
            base_commands + ["plan", "-out=plan.out"] + options + targets
        )

        # Assert that info log for successful execution was called
        mock_global_logger.info.assert_called_with("Terraform plan executed successfully.")

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    def test_run_terraform_plan_failure(self, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for failed plan execution
        targets = ["target1", "target2"]
        plan_output = "Terraform plan failed"
        mock_run_terraform_command.return_value = (plan_output, "", 1)  # Failure return code

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method
        handler.run_terraform_plan(targets)
        
        base_commands = handler._TerraformHandler__base_commands
        options = handler._TerraformHandler__options

        # Check that the plan command was executed with the expected arguments
        mock_run_terraform_command.assert_called_once_with(
            base_commands + ["plan", "-out=plan.out"] + options + targets
        )

        # Assert that error log for failed execution was called
        mock_global_logger.error.assert_called_with("Terraform plan failed.")

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    def test_run_terraform_plan_exception(self, mock_run_terraform_command, mock_global_logger):
        # Simulate an exception during the execution of terraform plan
        targets = ["target1", "target2"]
        mock_run_terraform_command.side_effect = Exception("Test exception")

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method
        handler.run_terraform_plan(targets)

        # Assert that the error log was called due to the exception
        mock_global_logger.error.assert_called_with("Error during plan operation: Test exception")

    ####### run_terraform_show #########

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.save_json_plan')  # Mock save_json_plan
    def test_run_terraform_show_success(self, mock_save_json_plan, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for successful terraform show command execution
        targets = ["target1", "target2"]
        plan_output = '{"key": "value"}'  # Mocked JSON output from terraform show
        mock_run_terraform_command.return_value = (plan_output, "", 0)  # Success return code

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method with a file path
        result = handler.run_terraform_show(file_path="output.json")
        base_commands = handler._TerraformHandler__base_commands

        # Check that the terraform show command was executed with the expected arguments
        mock_run_terraform_command.assert_called_once_with(
            base_commands + ["show", "-json", "plan.out"]
        )

        # Check if the output was saved
        mock_save_json_plan.assert_called_once_with({"key": "value"}, "output.json")

        # Assert that the result is the parsed JSON
        self.assertEqual(result, {"key": "value"})

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    def test_run_terraform_show_failure(self, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for failed terraform show command execution
        plan_output = "Error: Terraform show failed"
        mock_run_terraform_command.return_value = (plan_output, "Error details", 1)  # Failure return code

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method
        result = handler.run_terraform_show()
        base_commands = handler._TerraformHandler__base_commands
  
        # Check that the terraform show command was executed with the expected arguments
        mock_run_terraform_command.assert_called_once_with(
            base_commands + ["show", "-json", "plan.out"]
        )

        # Assert that error logs were called
        mock_global_logger.error.assert_any_call("Terraform show failed.")
        mock_global_logger.error.assert_any_call("Error details")

        # Assert that the result is None
        self.assertIsNone(result)

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    def test_run_terraform_show_exception(self, mock_run_terraform_command, mock_global_logger):
        # Simulate an exception during the execution of terraform show command
        mock_run_terraform_command.side_effect = Exception("Test exception")

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method
        result = handler.run_terraform_show()

        # Assert that the error log was called due to the exception
        mock_global_logger.error.assert_called_with("Error during `terraform show`: Test exception")

        # Assert that the result is None
        self.assertIsNone(result)

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.run_terraform_command')  # Mock run_terraform_command
    @patch('terraform_importer.handlers.terraform_handler.TerraformHandler.save_json_plan')  # Mock save_json_plan
    def test_run_terraform_show_no_file_path(self, mock_save_json_plan, mock_run_terraform_command, mock_global_logger):
        # Prepare mock data for successful terraform show command execution
        targets = ["target1", "target2"]
        plan_output = '{"key": "value"}'  # Mocked JSON output from terraform show
        mock_run_terraform_command.return_value = (plan_output, "", 0)  # Success return code

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method without a file path
        result = handler.run_terraform_show()
        base_commands = handler._TerraformHandler__base_commands

        # Check that the terraform show command was executed with the expected arguments
        mock_run_terraform_command.assert_called_once_with(
            base_commands + ["show", "-json", "plan.out"]
        )

        # Check if the output was not saved
        mock_save_json_plan.assert_not_called()

        # Assert that the result is the parsed JSON
        self.assertEqual(result, {"key": "value"})

    ####### save_json_plan #########

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('builtins.open', new_callable=mock_open)  # Mock open() function
    def test_save_json_plan_success(self, mock_open, mock_global_logger):
        # Prepare mock JSON data
        json_data = {"key": "value"}
        file_path = "plan.json"

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method to save the JSON data
        handler.save_json_plan(json_data, file_path)

        # Verify that open() was called with the correct file path and mode 'w'
        mock_open.assert_called_once_with(file_path, 'w')

        # Verify that json.dump was called with the correct arguments
        
        written_data = json.dumps(json_data, indent=4)  # Expected string with indentation and newlines
        written_content = ''.join([arg for call in mock_open().write.call_args_list for arg in call[0]])
        
        # Assert that the content written to the file matches the expected string
        self.assertEqual(written_content, written_data)
        # Verify that the info log was called after saving the file
        mock_global_logger.info.assert_called_with(f"Terraform plan JSON saved to {file_path}")

    @patch('terraform_importer.handlers.terraform_handler.global_logger')  # Mock global_logger
    @patch('builtins.open', new_callable=mock_open)  # Mock open() function
    def test_save_json_plan_failure(self, mock_open, mock_global_logger):
        # Prepare mock JSON data
        json_data = {"key": "value"}
        file_path = "plan.json"

        # Simulate an exception when opening the file (e.g., file write failure)
        mock_open.side_effect = IOError("Failed to write to file")

        # Create an instance of the class
        handler = TerraformHandler(self.mock_valid_folder)

        # Call the method to save the JSON data
        handler.save_json_plan(json_data, file_path)

        # Verify that the error log was called due to the exception
        mock_global_logger.error.assert_called_with(f"Failed to save Terraform plan JSON: Failed to write to file")

if __name__ == "__main__":
    unittest.main()
