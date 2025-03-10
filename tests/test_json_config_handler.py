import unittest
import json
import os
import tempfile
from pathlib import Path
from terraform_importer.handlers.json_config_handler import JsonConfigHandler
import pprint

class TestJsonConfigHandler(unittest.TestCase):
    def setUp(self):
        self.json_config = json.load(open("tests/assets/plan.json"))

    def test_replace_variables(self):
        variables = self.json_config["variables"]
        provider_config = self.json_config["configuration"]["provider_config"]
        replaced_provider_config = JsonConfigHandler.replace_variables(provider_config, variables)
        json.dump(replaced_provider_config, open("tests/assets/replaced_provider_config.json", "w"))
        
        # Helper function to check for ${var...} patterns in values
        def has_var_references(obj):
            if isinstance(obj, dict):
                return any(has_var_references(v) for v in obj.values())
            elif isinstance(obj, list):
                return any(has_var_references(item) for item in obj)
            elif isinstance(obj, str):
                return "${var." in obj
            return False
        
        self.assertFalse(has_var_references(replaced_provider_config), 
                        "Found unreplaced variable references in provider config")

    def test_extract_provider_config_keys(self):
        json_data = {
            "resource": {
                "aws_instance": {
                    "provider_config_key": "aws",
                    "instances": [
                        {"provider_config_key": "aws.us-east-1"},
                        {"provider_config_key": "aws.us-west-2"}
                    ]
                }
            }
        }

        result = JsonConfigHandler.extract_provider_config_keys(self.json_config["configuration"]["root_module"])
        # pprint.pprint(result)
        json.dump(result, open("tests/assets/provider_config_keys.json", "w"))
        # Result would be:
        # {
        #     "resource.aws_instance": "aws",
        #     "resource.aws_instance.instances[0]": "aws.us-east-1",
        #     "resource.aws_instance.instances[1]": "aws.us-west-2"
        # }

    def test_simplify_references(self):
        json_data = json.load(open("tests/assets/replaced_provider_config.json"))
        simplified_json_data = JsonConfigHandler.simplify_references(json_data)
        json.dump(simplified_json_data, open("tests/assets/simplified_provider_config.json", "w"))

    def test_simplify_constant_values(self):
        json_data = json.load(open("tests/assets/simplified_provider_config.json"))
        simplified_json_data = JsonConfigHandler.simplify_constant_values(json_data)
        json.dump(simplified_json_data, open("tests/assets/simplified_provider_config_constant_values.json", "w"))

if __name__ == "__main__":
    unittest.main()

