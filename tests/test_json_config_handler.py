import unittest
import json
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from terraform_importer.handlers.json_config_handler import JsonConfigHandler
import pprint

class TestJsonConfigHandler(unittest.TestCase):
    def setUp(self):
        self.json_config = json.load(open("plan.json"))

    def test_replace_variables(self):
        variables = self.json_config["variables"]
        provider_config = self.json_config["configuration"]["provider_config"]
        replaced_provider_config = JsonConfigHandler.replace_variables(provider_config, variables)
        #json.dump(replaced_provider_config, open("replaced_provider_config.json", "w"))
        
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

    ###### simpilfy_referance ######

    def test_simplify_references_no_references(self):
        input_data = {
            "key1": "value1",
            "key2": {
                "nested_key": "nested_value"
            }
        }
        expected_output = {
            "key1": "value1",
            "key2": {
                "nested_key": "nested_value"
            }
        }
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_references_single_reference(self):
        input_data = {
            "key1": {
                "references": [{"value": "simplified_value"}]
            },
            "key2": "value2"
        }
        expected_output = {
            "key1": "simplified_value",
            "key2": "value2"
        }
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_references_multiple_references(self):
        input_data = {
            "key1": {
                "references": [{"value": "value1"}, {"value": "value2"}]
            },
            "key2": "value2"
        }
        expected_output = {
            "key1": {
                "references": [{"value": "value1"}, {"value": "value2"}]
            },
            "key2": "value2"
        }
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_references_nested_structure(self):
        input_data = {
            "key1": {
                "nested_key": {
                    "references": [{"value": "nested_simplified_value"}]
                }
            }
        }
        expected_output = {
            "key1": {
                "nested_key": "nested_simplified_value"
            }
        }
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_references_empty_input(self):
        input_data = {}
        expected_output = {}
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_references_list_input(self):
        input_data = [
            {"references": [{"value": "simplified_value1"}]},
            {"key2": "value2"}
        ]
        expected_output = [
            "simplified_value1",
            {"key2": "value2"}
        ]
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_references_non_reference_value(self):
        input_data = {
            "key1": {
                "references": [{"wrong_key": "value1"}]
            }
        }
        expected_output = {
            "key1": {
                "references": [{"wrong_key": "value1"}]
            }
        }
        result = JsonConfigHandler.simplify_references(input_data)
        self.assertEqual(result, expected_output)

    ###### simplify_constant_values ######

    def test_simplify_constant_values_no_constant_value(self):
        input_data = {
            "key1": "value1",
            "key2": {
                "nested_key": "nested_value"
            }
        }
        expected_output = {
            "key1": "value1",
            "key2": {
                "nested_key": "nested_value"
            }
        }
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_constant_values_single_constant_value(self):
        input_data = {
            "key1": {
                "constant_value": "simplified_value"
            },
            "key2": "value2"
        }
        expected_output = {
            "key1": "simplified_value",
            "key2": "value2"
        }
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_constant_values_nested_constant_value(self):
        input_data = {
            "key1": {
                "nested_key": {
                    "constant_value": "nested_simplified_value"
                }
            }
        }
        expected_output = {
            "key1": {
                "nested_key": "nested_simplified_value"
            }
        }
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_constant_values_multiple_constant_values(self):
        input_data = {
            "key1": {
                "constant_value": "value1"
            },
            "key2": {
                "constant_value": "value2"
            }
        }
        expected_output = {
            "key1": "value1",
            "key2": "value2"
        }
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_constant_values_empty_input(self):
        input_data = {}
        expected_output = {}
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_constant_values_list_input(self):
        input_data = [
            {"constant_value": "simplified_value1"},
            {"key2": "value2"}
        ]
        expected_output = [
            "simplified_value1",
            {"key2": "value2"}
        ]
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

    def test_simplify_constant_values_non_constant_value_structure(self):
        input_data = {
            "key1": {
                "incorrect_key": "some_value"
            }
        }
        expected_output = {
            "key1": {
                "incorrect_key": "some_value"
            }
        }
        result = JsonConfigHandler.simplify_constant_values(input_data)
        self.assertEqual(result, expected_output)

   # ###### extract_provider_config_keys ######
#
   # def test_extract_provider_config_keys_no_provider_config_key(self):
   #     input_data = {
   #         "key1": "value1",
   #         "key2": {
   #             "nested_key": "nested_value"
   #         }
   #     }
   #     expected_output = {}
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
   # def test_extract_provider_config_keys_single_provider_config_key(self):
   #     input_data = {
   #         "module_calls": {
   #             "module1": {
   #                 "provider_config_key": "provider1"
   #             }
   #         }
   #     }
   #     expected_output = {
   #         "module1": "provider1"
   #     }
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
   # def test_extract_provider_config_keys_multiple_provider_config_keys(self):
   #     input_data = {
   #         "module_calls": {
   #             "module1": {
   #                 "provider_config_key": "provider1"
   #             },
   #             "module2": {
   #                 "provider_config_key": "provider2"
   #             }
   #         }
   #     }
   #     expected_output = {
   #         "module1": "provider1",
   #         "module2": "provider2"
   #     }
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
   # def test_extract_provider_config_keys_nested_provider_config_key(self):
   #     input_data = {
   #         "resources": [
   #             {
   #                 "name": "resource1",
   #                 "details": {
   #                     "provider_config_key": "provider1"
   #                 }
   #             },
   #             {
   #                 "name": "resource2",
   #                 "details": {
   #                     "provider_config_key": "provider2"
   #                 }
   #             }
   #         ]
   #     }
   #     expected_output = {
   #         "resources[0]": "provider1",
   #         "resources[1]": "provider2"
   #     }
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
   # def test_extract_provider_config_keys_mixed_data(self):
   #     input_data = {
   #         "module_calls": {
   #             "module1": {
   #                 "provider_config_key": "provider1"
   #             },
   #             "module2": {
   #                 "details": {
   #                     "provider_config_key": "provider2"
   #                 }
   #             }
   #         },
   #         "resources": [
   #             {
   #                 "name": "resource1",
   #                 "provider_config_key": "provider3"
   #             }
   #         ]
   #     }
   #     expected_output = {
   #         "module1": "provider1",
   #         "module2.details": "provider2",
   #         "resources[0]": "provider3"
   #     }
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
   # def test_extract_provider_config_keys_with_address_in_list(self):
   #     input_data = {
   #         "resources": [
   #             {
   #                 "address": "resource1_address",
   #                 "provider_config_key": "provider1"
   #             },
   #             {
   #                 "address": "resource2_address",
   #                 "provider_config_key": "provider2"
   #             }
   #         ]
   #     }
   #     expected_output = {
   #         "resource1_address": "provider1",
   #         "resource2_address": "provider2"
   #     }
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
   # def test_extract_provider_config_keys_empty_input(self):
   #     input_data = {}
   #     expected_output = {}
   #     result = JsonConfigHandler.extract_provider_config_keys(input_data)
   #     self.assertEqual(result, expected_output)
#
#
   
if __name__ == "__main__":
    unittest.main()

