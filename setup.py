#from distutils.core import setup
from setuptools import setup
from mr_repo.version import version
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as file:
        long_description = file.read()

setup(name='Mr-Repo',
      version=version,
      author='Ryan McGowan',
      author_email='ryan@ryanmcg.com',
      description='A very simple repo manager of repos.',
      long_description=long_description,
      url='http://pypi.python.org/pypi/Mr-Repo/' + version,
      install_requires=['PyYAML', 'GitPython'],
      packages=['mr_repo'],
      scripts=['mr-repo'],
      classifiers=['Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2']
      )
