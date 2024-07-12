# setup.py

from setuptools import setup, find_packages

setup(
    name="pyfsq",
    version="0.1.0",
    author="Thomas Stibor",
    author_email="t.stibor@gsi.de",
    description="Python-based console client and API for transferring data to FSQ server",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tstibor/pyfsq",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
