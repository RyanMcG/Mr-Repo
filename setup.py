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
      url='http://pypi.python.org/pypi/Mr-Repo/' + version,
      py_modules=['mr_repo'],
      scripts=['mr_repo'],
      requires=['PyYAML', 'GitPython'],
      classifiers=['Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2']
      )
