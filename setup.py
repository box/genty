# coding: utf-8

from __future__ import unicode_literals
from setuptools import setup, find_packages
from os.path import dirname, join


def main():
    base_dir = dirname(__file__)
    setup(
        name='genty',
        version='0.3.1',
        description='Allows you to run a test with multiple data sets',
        long_description=open(join(base_dir, 'README.rst')).read(),
        author='Box',
        author_email='oss@box.com',
        url='https://github.com/box/genty',
        license=open(join(base_dir, 'LICENSE')).read(),
        packages=find_packages(exclude=['test']),
        namespace_packages=[b'box', b'box.test'],
        test_suite='test',
        zip_safe=False,
        keywords=('genty', 'tests', 'generative'),
    )


if __name__ == '__main__':
    main()
