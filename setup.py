#from distutils.core import setup
from setuptools import setup

with open('README.rst') as file:
        long_description = file.read()

with open('VERSION.txt') as file:
        version = file.read().rstrip()

setup(name='Mr-Repo',
      version=version,
      author='Ryan McGowan',
      author_email='ryan@ryanmcg.com',
      description='A very simple repo manager of repos.',
      long_description=long_description,
      url='http://pypi.python.org/pypi/Mr-Repo/' + version,
      install_requires=['PyYAML', 'GitPython'],
      py_modules=['mr_repo'],
      scripts=['mr_repo'],
      classifiers=['Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2']
      )
