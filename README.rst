jupyterlite-xblock
==================

Xblock to integrate JupyterLite service with open edX

Installation
------------

    pip install jupyterlite-xblock

Usage
-----

In the Studio, go to the advanced settings of your course ("Settings" 🡒 "Advanced Settings"). In the "Advanced Module List" add "jupyterlite". Then hit "Save changes".

Add these settings to enable S3 Storage. Please make sure your bucket's CORS allow JupyterLite service URL

    XBLOCK_SETTINGS["JupterLiteXBlock"] = {
        "STORAGE_FUNC": "jupyterlitexblock.storage.s3",
        "S3_BUCKET_NAME": "YOUR_BUCKET_NAME_GOES_HERE"
    }
