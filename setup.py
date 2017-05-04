# coding=utf-8
from setuptools import setup
from os import path

__this_dir = path.abspath(path.dirname(__file__))

setup(
    name='clarindspace',
    version='0.1.0',
    description='clarin-dspace REST API examples',
    long_description='clarin-dspace REST API examples',
    url='https://github.com/vidiecan/pyclarindspace',
    author='CLARIN/LINDAT',
    author_email='lindat-technical@ufal.mff.cuni.cz',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['clarindspace'],
    install_requires=['requests', 'requests_toolbelt'],
)
