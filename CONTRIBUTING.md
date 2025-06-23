# Contributing to Terraform Importer

First off, thank you for considering contributing to Terraform Importer! It's people like you that make it such a great tool.

## Code of Conduct
This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### First Steps
We maintain a list of issues marked as `good first issue` that are ideal for getting started. Currently, our main focus is on expanding AWS resource support - you can find specific resource implementation tasks in our issues. These are perfect for:
- Developers familiar with AWS resources and Terraform
- Those looking to make their first open source contribution
- Anyone interested in infrastructure as code

Check out our [issues page](https://github.com/eyalya/terraform-importer/issues) and look for:
- Issues tagged with `good first issue`
- AWS resource implementation tasks
- Documentation improvements

### Reporting Bugs
Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include details about your configuration and environment

### Suggesting Enhancements
Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests
* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python styleguides
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Process

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`python -m unittest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/terraform-importer.git

# Add upstream remote
git remote add upstream https://github.com/eyalya/terraform-importer.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests
```bash
# Run all tests
python3 -m unittest tests

# Run specific test file
python3 -m unittest tests/test_specific.py

# Run with coverage report
python3 -m unittest --cov=terraform_importer tests/
```

## Styleguides

### Git Commit Messages
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide
* Follow PEP 8
* Use meaningful variable names
* Write docstrings for all public methods and classes
* Keep functions focused and small
* Use type hints where appropriate

## Additional Notes

### Issue and Pull Request Labels
* `bug`: Something isn't working
* `enhancement`: New feature or request
* `documentation`: Improvements or additions to documentation
* `good first issue`: Good for newcomers
* `help wanted`: Extra attention is needed
* `question`: Further information is requested

Thank you for contributing to Terraform Importer! 