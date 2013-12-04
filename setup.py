#/usr/bin/env python
import os
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

setup(
    name="will",
    description="A friendly python hipchat bot",
    author="Steven Skoczen",
    author_email="steven@greenkahuna.com",
    url="https://github.com/greenkahuna/will",
    version="0.1",
    packages=find_packages(),
)