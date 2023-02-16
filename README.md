## Cloud File Manager 

A CLI utility app to upload files to either Amazon S3 or Google Cloud Storage

#### Installation

`pip install file_uploader_cli-0.1-py3-none-any`

#### Usage

To use the file_manager app, run:

`file_manager [options]`

#### Available Options

```
--config: Path to the config file.

--directory: Directory from which to upload files to cloud.
```

#### Configuration

The file_manager CLI App can be configured by creating a config.ini file in the same directory as the file_manager_cli module.

#### sample config:
```
[s3]

access_key = aws_access_key

secret_key = secret_key

bucket_name = s3_bucket_name

extensions = s3_file_extentions

[gcs]

credentials_path = path/to/service_account_key.json

bucket_name = gcs_bucket_name

project_id = project_id

extensions = gcs_file_extentions
```

#### Testing

To run the test suite for the file_manager CLI App, run:

`pytest`
