import os
import tempfile
from will import VERSION
from fabric.api import *

SITE_DIR = "site"
WHITELIST_DIRS = [".git", ]
WHITELIST_FILES = [".gitignore", ]

SANITY_CHECK_PROJECT_FILES = ["fabfile.py", "setup.py", "mkdocs.yml"]
SANITY_CHECK_BUILD_FILES = ["index.html", "js", "css"]

CTAG = os.environ.get("CTAG", "")

DOCKER_BUILDS = [
    {
        "name": "heywill/will:python2.7%(CTAG)s" % os.environ,
        "dir": "will/will-py2/",
    },
    {
        "name": "heywill/will:python3.7%(CTAG)s" % os.environ,
        "dir": "will/will-py3/",
    },
]
DOCKER_PATH = os.path.join(os.getcwd(), "docker")


def _splitpath(path):
    path = os.path.normpath(path)
    return path.split(os.sep)


def tag_release():
    # Tag the release:
    local("git tag %s" % VERSION)
    local("git push --tags")


def upload_release():
    local("python setup.py sdist upload")


def release():
    deploy_docs()
    upload_release()
    tag_release()


def deploy_docs():
    # Sanity check dir.
    root_dir = os.getcwd()
    assert all([os.path.exists(os.path.join(root_dir, f)) for f in SANITY_CHECK_PROJECT_FILES])

    local("rm -rf %s" % SITE_DIR)
    local("mkdocs build")
    tempdir = tempfile.mkdtemp()

    local("mv %s/* %s" % (SITE_DIR, tempdir))

    current_branch = local("git rev-parse --abbrev-ref HEAD", capture=True)
    last_commit = local("git log -1 --pretty=\%B", capture=True)

    # Add the new site to build
    local("git checkout gh-pages")

    # Sanity check dir.
    root_dir = os.getcwd()
    assert all([os.path.exists(os.path.join(root_dir, f)) for f in SANITY_CHECK_BUILD_FILES])

    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in files:
            if name not in WHITELIST_FILES and not any([r in WHITELIST_DIRS for r in _splitpath(root)]):
                # print("removing %s" % (os.path.join(root, name)))
                os.remove(os.path.join(root, name))
        for name in dirs:
            if name not in WHITELIST_DIRS and not any([r in WHITELIST_DIRS for r in _splitpath(root)]):
                print("removing %s" % (os.path.join(root, name)))
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    # Handle symlinks
                    os.remove(os.path.join(root, name))

    local("cp -rv %s/* ." % tempdir)
    with settings(warn_only=True):
        result = local("git diff --exit-code")

    if result.return_code != 0:
        local("git add -A .")
        local("git commit -m 'Auto-update of docs: %s'" % last_commit)
        local("git push")
    else:
        print("No changes to the docs.")
    local("git checkout %s" % current_branch)


def docker_build():
    with lcd(DOCKER_PATH):
        for c in DOCKER_BUILDS:
            local("docker build -t %(name)s %(dir)s" % c)


def docker_tag():
    with lcd(DOCKER_PATH):
        for c in DOCKER_BUILDS:
            local("docker tag %(name)s %(dir)s" % c)


def docker_push():
    with lcd(DOCKER_PATH):
        local("docker push heywill/will-base:latest")
        local("docker push heywill/will:latest")


def docker_deploy():
    docker_build()
    docker_tag()
    docker_push()
