import os
import tempfile
from invoke import task
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


def tag_release(ctx):
    # Tag the release:
    ctx.run("git tag %s" % VERSION)
    ctx.run("git push --tags")


def upload_release(ctx):
    ctx.run("python setup.py sdist upload")


@task
def release(ctx):
    deploy_docs(ctx)
    upload_release(ctx)
    tag_release(ctx)


def deploy_docs(ctx):
    # Sanity check dir.
    root_dir = os.getcwd()
    assert all([os.path.exists(os.path.join(root_dir, f)) for f in SANITY_CHECK_PROJECT_FILES])

    ctx.run("rm -rf %s" % SITE_DIR)
    ctx.run("mkdocs build")
    tempdir = tempfile.mkdtemp()

    ctx.run("mv %s/* %s" % (SITE_DIR, tempdir))

    current_branch = ctx.run("git rev-parse --abbrev-ref HEAD", capture=True)
    last_commit = ctx.run("git log -1 --pretty=\%B", capture=True)

    # Add the new site to build
    ctx.run("git checkout gh-pages")

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

    ctx.run("cp -rv %s/* ." % tempdir)
    result = ctx.run("git diff --exit-code", warn_only=True)

    if result.return_code != 0:
        ctx.run("git add -A .")
        ctx.run("git commit -m 'Auto-update of docs: %s'" % last_commit)
        ctx.run("git push")
    else:
        print("No changes to the docs.")
    ctx.run("git checkout %s" % current_branch)


@task
def docker_build(ctx):
    print("Building Docker Images...")
    with ctx.cd(DOCKER_PATH):
        for b in DOCKER_BUILDS:
            ctx.run("docker build -t %(ctagname)s %(dir)s" % b)


def docker_tag(ctx):
    print("Building Docker Releases...")
    with ctx.cd(DOCKER_PATH):
        for b in DOCKER_BUILDS:
            ctx.run("docker tag %(ctagname)s %(name)s" % b)


def docker_push(ctx):
    print("Pushing Docker to Docker Cloud...")
    with ctx.cd(DOCKER_PATH):
        ctx.run("docker login -u $DOCKER_USER -p $DOCKER_PASS")
        ctx.run("docker push heywill/will:python2.7")
        ctx.run("docker push heywill/will:python3.7")
        ctx.run("docker push heywill/will:latest")


@task
def docker_deploy(ctx):
    docker_build(ctx)
    docker_tag(ctx)
    docker_push(ctx)
