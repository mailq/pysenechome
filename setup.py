#!/usr/bin/env python
"""pysenechome library setup."""
from pathlib import Path
from setuptools import setup

VERSION = "0.0.1"
URL = "https://github.com/mailq/pysenechome"

setup(
    name="pysenechome",
    version=VERSION,
    description="Library to interface a SENEC.Home battery API",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url=URL,
    download_url="{}/tarball/{}".format(URL, VERSION),
    author="Marcel Lohmann",
    author_email="programming@malowa.de",
    license="MIT",
    packages=["pysenechome"],
    install_requires=["aiohttp>3,<4", "async_timeout>3,<4", "attrs>18"],
    zip_safe=True,
)
