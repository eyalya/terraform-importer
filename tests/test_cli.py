import sys
import unittest
from unittest.mock import patch
from terraform_importer.cli import TerraformImporterCLI

class TestParseArgs(unittest.TestCase):
    @patch("os.path.isdir", return_value=True)  # Mocking os.path.isdir
    @patch("sys.argv", new=["prog", "--config", "./fake-dir", "--log-level", "DEBUG"])  # Mocking sys.argv
    def test_parse_args_basic(self, mock_isdir):
        cli = TerraformImporterCLI()  # Instantiate the class
        args = cli.parse_args()  # Call the method to parse args
        
        # Assert the parsed arguments
        self.assertEqual(args.config, "./fake-dir")
        self.assertEqual(args.log_level, "DEBUG")
        self.assertEqual(args.option, [])
        self.assertEqual(args.target, [])

if __name__ == "__main__":
    unittest.main()
