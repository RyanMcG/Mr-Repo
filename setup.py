#from distutils.core import setup
from setuptools import setup
import mr_repo
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as \
        description_file:
    long_description = description_file.read()
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as \
        requirements_file:
    requirements = [line.rstrip() for line in requirements_file]


setup(name='Mr-Repo',
      version=mr_repo.version,
      author='Ryan McGowan',
      author_email='ryan@ryanmcg.com',
      description=mr_repo.__doc__,
      long_description=long_description,
      url='http://pypi.python.org/pypi/Mr-Repo/' + mr_repo.version,
      install_requires=requirements,
      packages=['mr_repo'],
      entry_points={
          'console_scripts': [
              'mr_repo = mr_repo.main:main'
          ]
      },
      classifiers=['Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2']
      )
