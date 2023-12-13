"""
Define any custom storage backends here
"""
from storages.backends.s3boto3 import S3Boto3Storage


class S3JupyterLiteStorage(S3Boto3Storage):
    """
    S3 backend for jupyterlite. Gives ability to set a custom bucket 
    for jupyterlite notebooks
    """

    def __init__(self, xblock, bucket_name=None):
        self.xblock = xblock
        super().__init__(
            bucket_name=bucket_name,
            querystring_auth=False,
        )


def s3(xblock, bucket_name=None):
    """
    Creates and returns an instance of the S3JupyterLiteStorage class.

    This function takes an xblock instance as its argument and returns an instance
    of the S3JupyterLiteStorage class. The S3JupyterLiteStorage provides S3 storage 
    functionality specific to JupyterLite XBlock.

    Args:
        xblock (XBlock): An instance of the JupyterLite XBlock.
        bucket_name (String): Name of the bucket where assets will be uploaded

    Returns:
        S3JupyterLiteStorage: An instance of the S3JupyterLiteStorage class.
    """
    
    return S3JupyterLiteStorage(
        xblock=xblock,
        bucket_name=bucket_name,
    )
