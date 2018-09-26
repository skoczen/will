#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages
from will import __name__ as PACKAGE_NAME
from will import VERSION

DESCRIPTION = "A friendly python hipchat bot"
ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)
REQS_DIR = os.path.join(ROOT_DIR, "will", "requirements")

install_requires = []
dependency_links = []
with open("requirements.txt", "r+") as f:
    for line in f.readlines():
        if line[0] == "-":
            continue
        install_requires.append(line.strip())

for req_file in ["base.txt", "slack.txt", "hipchat.txt", "rocketchat.txt"]:
    with open(os.path.join(REQS_DIR, req_file), "r+") as f:
        for line in f.readlines():
            if (
                (line.startswith("-") and not line.startswith("-e"))
                or line.startswith("#")
            ):
                continue

            if "-e" in line:
                line = line.replace("-e", "")
                dependency_links.append(line)
                line = line.split("#")[-1].split("=")[-1]

            install_requires.append(line.strip())


tests_require = [
    'pytest==3.8.1',
    'pytest-cov',
    'pytest-runner',
    'mock'
]

setup_requires = []
needs_pytest = set(('pytest', 'test', 'ptr')).intersection(sys.argv)

if needs_pytest:
    setup_requires.append('pytest-runner')


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError, RuntimeError):
    try:
        import os
        long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
    except:
        long_description = DESCRIPTION + '\n'

setup(
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    long_description=long_description,
    author="Steven Skoczen",
    author_email="skoczen@gmail.com",
    url="https://github.com/skoczen/will",
    version=VERSION,
    download_url=['https://github.com/skoczen/will/tarball/%s' % VERSION, ],
    install_requires=install_requires,
    dependency_links=dependency_links,
    setup_requires=setup_requires,
    tests_require=tests_require,
    packages=find_packages(),
    include_package_data=True,
    keywords=["chatbot", "bot", "ai", "slack", "hipchat", "rocketchat", "stride"],
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
        "Framework :: Robot Framework :: Tool",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': ['generate_will_project = will.scripts.generate_will_project:main'],
    },

)
