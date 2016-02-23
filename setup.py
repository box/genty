# coding: utf-8

from __future__ import absolute_import, unicode_literals

from codecs import open   # pylint:disable=redefined-builtin
from collections import defaultdict
from os.path import dirname, join
import sys

from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Operating System :: OS Independent',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
]


def main():
    base_dir = dirname(__file__)
    requirements = ['six']
    test_requirements = []
    extra_requirements = defaultdict(list)
    conditional_dependencies = {
        # Newer versions of pip and wheel, which support PEP 426, allow
        # environment markers for conditional dependencies to use operators
        # such as `<` and `<=` [1]. However, older versions of pip and wheel
        # only support PEP 345, which only allows operators `==` and `in` (and
        # their negations) along with string constants [2]. To get the widest
        # range of support, we'll only use the `==` operator, which means
        # explicitly listing all supported Python versions that need the extra
        # dependencies.
        #
        # [1] <https://www.python.org/dev/peps/pep-0426/#environment-markers>
        # [2] <https://www.python.org/dev/peps/pep-0345/#environment-markers>
        'ordereddict': ['2.6'],   # < 2.7
    }
    for requirement, python_versions in conditional_dependencies.items():
        for python_version in python_versions:
            # <https://wheel.readthedocs.org/en/latest/#defining-conditional-dependencies>
            python_conditional = 'python_version=="{0}"'.format(python_version)
            key = ':{0}'.format(python_conditional)
            extra_requirements[key].append(requirement)
    if sys.version_info[:2] == (2, 6):
        test_requirements.append('unittest2')
    setup(
        name='genty',
        version='1.3.2',
        description='Allows you to run a test with multiple data sets',
        long_description=open(join(base_dir, 'README.rst'), encoding='utf-8').read(),
        author='Box',
        author_email='oss@box.com',
        url='https://github.com/box/genty',
        license='Apache Software License, Version 2.0, http://www.apache.org/licenses/LICENSE-2.0',
        packages=find_packages(exclude=['test']),
        test_suite='test',
        zip_safe=False,
        keywords=('genty', 'tests', 'generative', 'unittest'),
        classifiers=CLASSIFIERS,
        install_requires=requirements,
        extras_require=extra_requirements,
        tests_require=test_requirements,
    )


if __name__ == '__main__':
    main()
