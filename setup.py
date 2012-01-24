from distutils.core import setup
from mr_repo import version

with open('README.rst') as file:
        long_description = file.read()

setup(name='Mr-Repo',
      version=version,
      author='Ryan McGowan',
      author_email='ryan@ryanmcg.com',
      description='A very simple repo manager of repos.',
      long_description=long_description,
      url='http://packages.python.org/Mr-Repo',
      py_modules=['mr_repo'],
      requires=['PyYAML']
      )
