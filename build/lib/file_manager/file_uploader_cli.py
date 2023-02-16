import os
import sys
import boto3
from google.cloud import storage
import click
import configparser
import logging


# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# StreamHandler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

# FileHandler
fh = logging.FileHandler('file_uploader.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class FileUploader:
    """
    A class to upload files to either Amazon S3 or Google Cloud Storage.

    Attributes:
        s3_access_key (str): The access key for the Amazon S3 bucket.
        s3_secret_key (str): The secret key for the Amazon S3 bucket.
        s3_bucket_name (str): The name of the Amazon S3 bucket to upload files to.
        s3_region (str): The region where the Amazon S3 bucket is located.
        gcs_credentials_path (str): The path to the Google Cloud Storage credentials file.
        gcs_bucket_name (str): The name of the Google Cloud Storage bucket to upload files to.
        file_extensions (list): A list of file extensions to upload.
    """

    def __init__(
        self,
        s3_access_key=None,
        s3_secret_key=None,
        s3_bucket_name=None,
        gcs_credentials_path=None,
        gcs_project_id=None,
        gcs_bucket_name=None,
        s3_file_extensions=None,
        gcs_file_extensions=None
    ):

        # AWS s3 configuration
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key
        self.s3_bucket_name = s3_bucket_name

        # Google Cloud Storage configuration
        self.gcs_project_id = gcs_project_id
        self.gcs_bucket_name = gcs_bucket_name

        # Files configuration
        self.s3_file_extensions = s3_file_extensions
        self.gcs_file_extensions = gcs_file_extensions
        self.file_extensions = s3_file_extensions + gcs_file_extensions

        # Initialize AWS S3 client
        self.s3 = boto3.resource(
            's3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key)

        # Initialize Google Cloud Storage client
        self.gcs = storage.Client.from_service_account_json(
            gcs_credentials_path)

    def upload_files(self, directory):
        """
        Walk through the specified directory and upload all files with allowed extensions
        to either AWS S3 or Google Cloud Storage based on the file extension.

        Args:
            directory (str): Path to the directory to be uploaded.

        Return:
            None

        Raises:
            Exception: If an error occurs during the file upload process.
        """

        for subdir, dirs, files in os.walk(directory):
            for file in files:
                file_extension = os.path.splitext(file)[1][1:].lower()
                if file_extension in self.file_extensions:
                    file_path = os.path.join(subdir, file)
                    # check if the file extension is appropriate for uploading to s3
                    if file_extension in self.s3_file_extensions:
                        try:
                            self.upload_to_s3(file_path, file)
                            logger.info(
                                f'Successfully uploaded {file} to AWS S3\'s {self.s3_bucket_name} bucket.')
                        except Exception as e:
                            logger.error(
                                f'Error uploading {file} to AWS S3\'s {self.s3_bucket_name} bucket: {e}')
                    # check if the file extension is appropriate for uploading to gcs
                    elif file_extension in self.gcs_file_extensions:
                        try:
                            self.upload_to_gcs(file_path, file)
                            logger.info(
                                f'Successfully uploaded {file} to Google Cloud Storage\'s {self.gcs_bucket_name} bucket.')
                        except Exception as e:
                            logger.error(
                                f'Error uploading {file} to Google Cloud Storage\'s {self.s3_bucket_name} bucket: {e}')

    def upload_to_s3(self, file_path: str, file_name: str) -> None:
        """
        Uploads a file to AWS S3.

        Args:
            file_path (str): The full path to the local file to upload.
            file_name (str): The desired filename to use when uploading the file to S3.

        Returns:
            None
        """
        self.s3.Bucket(self.s3_bucket_name).upload_file(file_path, file_name)

    def upload_to_gcs(self, file_path: str, file_name: str) -> None:
        """
        Uploads a file to Google Cloud Storage bucket.

        Args:
            file_path (str): The full path to the local file to upload.
            file_name (str): The desired filename to use when uploading the file to Google Cloud Storage.

        Returns:
            None
        """
        bucket = self.gcs.get_bucket(self.gcs_bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_filename(file_path)


@click.command()
@click.option('--config', '-c', default='config.ini', help='Path to configuration file')
@click.option('--directory', '-d', default=os.getcwd(), help='Directory to upload files from')
def cli(config, directory):
    """
    A command-line interface to upload files to AWS S3 or Google Cloud Storage.

    The function reads the configuration file specified by `config`, then extracts the necessary parameters to
    initialize the `FileUploader` class. The `FileUploader` instance uploads files found under `directory` with
    allowed extensions specified in the configuration file. If `directory` is not provided, the current working
    directory is used.

    Args:
        config (str): Path to configuration file.
        directory (str): Directory to upload files from.

    Returns:
        None
    """

    # Read configuration file
    config_parser = configparser.ConfigParser()
    config_parser.read(config)

    s3_access_key = config_parser.get('s3', 'access_key')
    s3_secret_key = config_parser.get('s3', 'secret_key')
    s3_bucket_name = config_parser.get('s3', 'bucket_name')
    gcs_credentials_path = config_parser.get('gcs', 'credentials_path')
    gcs_project_id = config_parser.get('gcs', 'project_id')
    gcs_bucket_name = config_parser.get('gcs', 'bucket_name')
    s3_file_extensions = config_parser.get('s3', 'extensions').split(',')
    gcs_file_extensions = config_parser.get('gcs', 'extensions').split(',')

    uploader = FileUploader(
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_bucket_name=s3_bucket_name,
        gcs_credentials_path=gcs_credentials_path,
        gcs_project_id=gcs_project_id,
        gcs_bucket_name=gcs_bucket_name,
        s3_file_extensions=s3_file_extensions,
        gcs_file_extensions=gcs_file_extensions
    )

    uploader.upload_files(directory)


if __name__ == '__main__':
    cli()
