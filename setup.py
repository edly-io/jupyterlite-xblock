"""Setup for Jupyterlite XBlock."""


import os

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='jupyterlite-xblock',
    version='16.0.8',
    description='Jupyterlite XBlock to embed jupyterlite service inside open edX',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',    
    license='AGPL v3',
    packages=[
        'jupyterlitexblock',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'jupyterlite = jupyterlitexblock:JupterLiteXBlock',
        ]
    },
    package_data=package_data("jupyterlitexblock", ["static", "public", "locale"]),
)
