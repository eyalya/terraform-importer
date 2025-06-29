from setuptools import setup, find_packages

setup(
    name="terraform_importer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'terraform-importer=terraform_importer.main:main'
        ]
    },
)
