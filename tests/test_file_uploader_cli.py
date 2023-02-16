import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from file_manager.file_uploader_cli import FileUploader


@pytest.fixture
def file_uploader():
    return FileUploader(
        s3_access_key='access_key',
        s3_secret_key='secret_key',
        s3_bucket_name='test_bucket',
        gcs_credentials_path='credentials.json',
        gcs_project_id='test_project',
        gcs_bucket_name='test_bucket',
        s3_file_extensions=['txt'],
        gcs_file_extensions=['jpg']
    )


def test_upload_to_s3(file_uploader):
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b'Test file contents')
        temp_file.flush()
        file_name = os.path.basename(temp_file.name)

        s3_mock = MagicMock()
        file_uploader.s3 = s3_mock

        file_uploader.upload_to_s3(temp_file.name, file_name)

        s3_mock.Bucket.assert_called_with(file_uploader.s3_bucket_name)
        s3_mock.Bucket.return_value.upload_file.assert_called_with(
            temp_file.name, file_name
        )


def test_upload_to_gcs(file_uploader):
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b'Test file contents')
        temp_file.flush()
        file_name = os.path.basename(temp_file.name)

        bucket_mock = MagicMock()
        blob_mock = MagicMock()
        file_uploader.gcs.get_bucket = MagicMock(return_value=bucket_mock)
        bucket_mock.blob = MagicMock(return_value=blob_mock)

        file_uploader.upload_to_gcs(temp_file.name, file_name)

        file_uploader.gcs.get_bucket.assert_called_with(
            file_uploader.gcs_bucket_name)
        bucket_mock.blob.assert_called_with(file_name)
        blob_mock.upload_from_filename.assert_called_with(temp_file.name)


def test_upload_files(file_uploader):
    with tempfile.TemporaryDirectory() as temp_dir:
        # create a file with a valid extension for s3
        with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
            f.write('file1 contents')

        # create a file with a valid extension for gcs
        with open(os.path.join(temp_dir, 'file2.jpg'), 'w') as f:
            f.write('file2 contents')

        # create a file with an invalid extension
        with open(os.path.join(temp_dir, 'file3.pdf'), 'w') as f:
            f.write('file3 contents')

        with patch.object(file_uploader, 'upload_to_s3') as s3_mock, \
                patch.object(file_uploader, 'upload_to_gcs') as gcs_mock:

            file_uploader.upload_files(temp_dir)

            s3_mock.assert_called_once_with(
                os.path.join(temp_dir, 'file1.txt'), 'file1.txt')
            gcs_mock.assert_called_once_with(
                os.path.join(temp_dir, 'file2.jpg'), 'file2.jpg')
            assert s3_mock.call_count == 1
            assert gcs_mock.call_count == 1
