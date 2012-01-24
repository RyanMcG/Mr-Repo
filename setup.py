from distutils.core import setup
from mr_repo import version

setup(name='Mr-Repo',
      version=version,
      author='Ryan McGowan',
      author_email='ryan@ryanmcg.com',
      description='A very simple repo manager of repos.',
      url='http://packages.python.org/Mr-Repo',
      py_modules=['mr_repo'],
      requires=['PyYAML']
      )
