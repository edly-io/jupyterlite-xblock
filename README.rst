# jupyterlite-xblock
Xblock to integrate JupyterLite service with open edX


Add these settings to enable S3 Storage. Please make sure your bucket's CORS allow Jupyter service URL

    XBLOCK_SETTINGS["JupterLiteXBlock"] = {
        "STORAGE_FUNC": "jupyterlitexblock.storage.s3",
        "S3_BUCKET_NAME": "edly-scorm-bucket"
    }


Add `jupyterlite` in Advanced Settings -> Advanced Module List and the add J