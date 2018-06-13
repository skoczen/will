import os
import tempfile
from fabric.api import *
from will import VERSION

SITE_DIR = "site"
WHITELIST_DIRS = [".git", ]
WHITELIST_FILES = [".gitignore", ]

SANITY_CHECK_PROJECT_FILES = ["fabfile.py", "setup.py", "mkdocs.yml"]
SANITY_CHECK_BUILD_FILES = ["index.html", "js", "css"]

CTAG = os.environ.get("CTAG", "")

DOCKER_BUILDS = [
    {
        "ctagname": "heywill/will:python2.7%s" % CTAG,
        "name": "heywill/will:python2.7" % os.environ,
        "dir": "will/will-py2/",
    },
    {
        "ctagname": "heywill/will:python2.7%s" % CTAG,
        "name": "heywill/will:latest" % os.environ,
        "dir": "will/will-py2/",
    },
    {
        "ctagname": "heywill/will:python3.7%s" % CTAG,
        "name": "heywill/will:python3.7" % os.environ,
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


@task
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
    result = local("git diff --exit-code", warn_only=True)

    if result.return_code != 0:
        local("git add -A .")
        local("git commit -m 'Auto-update of docs: %s'" % last_commit)
        local("git push")
    else:
        print("No changes to the docs.")
    local("git checkout %s" % current_branch)


@task
def docker_build():
    print("Building Docker Images...")
    with lcd(DOCKER_PATH):
        for b in DOCKER_BUILDS:
            local("docker build -t %(ctagname)s %(dir)s" % b)


def docker_tag():
    print("Building Docker Releases...")
    with lcd(DOCKER_PATH):
        for b in DOCKER_BUILDS:
            local("docker tag %(ctagname)s %(name)s" % b)


def docker_push():
    print("Pushing Docker to Docker Cloud...")
    with lcd(DOCKER_PATH):
        local("docker login -u $DOCKER_USER -p $DOCKER_PASS")
        local("docker push heywill/will:python2.7")
        local("docker push heywill/will:python3.7")
        local("docker push heywill/will:latest")


@task
def docker_deploy():
    docker_build()
    docker_tag()
    docker_push()
