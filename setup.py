#  SugarCRM
#  --------
#  Python client for SugarCRM API.
#
#  Authors:  Festum <festum@g.pl>
#  Website: https://github.com/Festum/sugarcrm
#  Forked: https://github.com/ryanss/sugarcrm
#  License: MIT (see LICENSE file)
#  Version: 0.1.3 (Oct 22, 2017)


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='sugarcrm',
    version='0.1.2',
    author='ryanss',
    author_email='ryanssdev@icloud.com',
    url='https://github.com/ryanss/sugarcrm',
    license='MIT',
    py_modules=['sugarcrm'],
    description='Python client for SugarCRM API',
    long_description=open('README.rst').read(),
    install_requires=['requests'],
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
