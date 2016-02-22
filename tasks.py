from invoke import run, task


@task
def release():
    """
    Publishes the project on PyPI.

    We have automatic publishing enabled on TRAVIS build, so this is not
    necessary... but I'll keep here for reference.
    """
    run("python setup.py sdist upload")


@task
def test():
    """
    Executes all the tests.
    """
    run("python setup.py pytest")


@task
def travis_setpass():
    """
    Stores the PyPI password (encrypted) in the .travis.yml file.
    """
    print("travis encrypt --add deploy.password")


