"""
setup.py

Basic setup file to enable pip install
See:
    https://pythonhosted.org/setuptools/
    https://bitbucket.org/pypa/setuptools


python setup.py register sdist upload

"""
import sys
import os
from setuptools import setup, find_packages

v = sys.version_info
if sys.version_info < (3, 5):
    msg = "FAIL: Requires Python 3.5 or later, but setup.py was run using {}.{}.{}"
    v = sys.version_info
    print(msg.format(v.major, v.minor, v.micro))
    print("NOTE: Installation failed. Run setup.py using python3")
    sys.exit(1)

# Change to repo source directory prior to running any command
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're probably being frozen, and __file__ triggered this NameError
    # Work around this
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)

METADATA = os.path.join(SETUP_DIRNAME, 'ioserve', '__metadata__.py')
# Load the metadata using exec() so we don't trigger an import of .__init__
exec(compile(open(METADATA).read(), METADATA, 'exec'))

REQUIRES = ['ioflo']

setup(
    name='ioserve',
    version=__version__,
    description='Micro-Services with Ioflo Example',
    long_description='Using ioflo http client and http wisgi servers',
    url='https://github.com/ioflo/ioserve',
    download_url='https://github.com/ioflo/ioserve.git',
    author=__author__,
    author_email='smith.samuel.m@gmail.com',
    license=__license__,
    keywords=('Micro-Service Ioflo'),
    packages=find_packages(exclude=['test', 'test.*',
                                      'docs', 'docs*',
                                      'log', 'log*',]),
    package_data={
        '':       ['*.txt',  '*.md', '*.rst', '*.json', '*.conf', '*.html',
                   '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL'],
        'ioserve': ['flo/plan/*.flo', 'flo/plan/*/*.flo',
                  'flo/plan/*.txt', 'flo/plan/*/*.txt',],},
    install_requires=REQUIRES,
    extras_require={},
    scripts=['scripts/ioserve',])

