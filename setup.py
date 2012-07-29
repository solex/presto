from setuptools import setup, find_packages

version = __import__('presto').get_version()

setup(name='pRESTo',
      version=version,
      description='Command line Rest Api client',
      long_description='',
      author='Nikolay Melnik',
      author_email='nmelnik@odeskps.com',
      packages = find_packages(exclude=['tests']),
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
