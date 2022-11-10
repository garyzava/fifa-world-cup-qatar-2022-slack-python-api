from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Package meta-data.
NAME = 'my-fifa-2022-package'
DESCRIPTION = 'Python script that reads data from the FIFAs API for World Cup Qatar 2022, then post the data on a slack channel through a slack bot (slack app)'
URL = 'https://github.com/garyzava/fifa-world-cup-qatar-2022-slack-python-api/'
EMAIL = 'garyzava@umich.edu'
AUTHOR = 'garyzava'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'

# What packages are required for this module to be executed?
REQUIRED = requirements

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    #py_modules=['src'],

    #entry_points={
    #    'console_scripts': ['hello-world-dist-cli = src.main:say_hello'],
    #},
    install_requires=REQUIRED,
    #extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
)