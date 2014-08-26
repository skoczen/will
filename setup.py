#/usr/bin/env python
import os
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)
VERSION = "0.5.5"

reqs = []
with open("requirements.txt", "r+") as f:
    for line in f.readlines():
        reqs.append(line.strip())

try:
   import pypandoc
   long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''   

setup(
    name="will",
    description="A friendly python hipchat bot",
    long_description=long_description,
    author="Steven Skoczen",
    author_email="skoczen@gmail.com",
    url="https://github.com/skoczen/will",
    version=VERSION,
    download_url = ['https://github.com/skoczen/will/tarball/%s' % VERSION, ],
    install_requires=reqs,
    packages=find_packages(),
    include_package_data=True,
    keywords = ["hipchat", "bot"],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': ['generate_will_project = will.scripts.generate_will_project:main'],
    },

)
