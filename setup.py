from setuptools import setup, find_packages
from presto import version

ver = version.get_version()

setup(name='pRESTo',
      version=ver,
      description='Command line Rest Api client',
      long_description='',
      author='Nikolay Melnik',
      author_email='nmelnik@odeskps.com',
      packages = find_packages(exclude=['tests']),
      package_data = { 
                   'presto': [ 'presto.cfg'],
                   },
      install_requires = ['docopt', 'json_tools', 'oauthlib', ],
      classifiers=['Development Status :: 1 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
     scripts = ['presto-cfg.py',
                'presto-url.py']
)
