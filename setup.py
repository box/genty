# coding: utf-8

from __future__ import unicode_literals
from os.path import dirname, join
from setuptools import setup, find_packages
from sys import version_info

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: OS Independent',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
]


def main():
    base_dir = dirname(__file__)
    requirements = ['six']
    test_requirements = []
    if version_info[0] == 2 and version_info[1] == 6:
        requirements.append('ordereddict')
        test_requirements.append('unittest2')
    setup(
        name='genty',
        version='1.2.0',
        description='Allows you to run a test with multiple data sets',
        long_description=open(join(base_dir, 'README.rst')).read(),
        author='Box',
        author_email='oss@box.com',
        url='https://github.com/box/genty',
        license=open(join(base_dir, 'LICENSE')).read(),
        packages=find_packages(exclude=['test']),
        test_suite='test',
        zip_safe=False,
        keywords=('genty', 'tests', 'generative', 'unittest'),
        classifiers=CLASSIFIERS,
        install_requires=requirements,
        tests_require=test_requirements,
    )


if __name__ == '__main__':
    main()
