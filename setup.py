from setuptools import setup, find_packages

setup(
    name="terraform_importer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'terraform-import-tool=main:main'
        ]
    },
)
