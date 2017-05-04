# coding=utf-8
import clarindspace
from setuptools import setup
from os import path

setup(
    name=clarindspace.__title__,
    version=clarindspace.__version__,
    description='clarin-dspace REST API examples',
    long_description='clarin-dspace REST API examples',
    url='https://github.com/vidiecan/pyclarindspace',
    author='CLARIN/LINDAT',
    author_email='lindat-technical@ufal.mff.cuni.cz',
    license=clarindspace.__license__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    packages=['clarindspace'],
    install_requires=['requests', 'requests_toolbelt'],
)
