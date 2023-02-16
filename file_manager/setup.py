from setuptools import setup, find_packages

setup(
    name='file_uploader_cli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'google-cloud-storage',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'file_manager=file_manager.file_uploader_cli:cli'
        ]
    }
)
