#!/usr/bin/env python

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2013, The Materials Virtual Lab"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "ongsp@ucsd.edu"
__date__ = "Jan 31, 2014"

from setuptools import setup, find_packages
import os

if __name__ == "__main__":
    setup(
        name='fireworks-vasp',
        version='0.1',
        description='VASP Plugin for fireworks',
        long_description='VASP Plugin for fireworks',
        url='https://github.com/materialsproject/fireworks',
        author="Shyue Ping Ong",
        author_email='anubhavster@gmail.com',
        license='MIT',
        packages=find_packages(),
        package_data={'fireworks':['user_objects/queue_adapters/*.txt']},
        zip_safe=False,
        install_requires=['pymatgen>=2.9.0', 'custodian>=0.7.0',
                          'fireworks>=0.66'],
        classifiers=['Programming Language :: Python :: 2.7',
                     'Development Status :: 4 - Beta',
                     'Intended Audience :: Science/Research',
                     'Intended Audience :: System Administrators',
                     'Intended Audience :: Information Technology',
                     'Operating System :: OS Independent',
                     'Topic :: Other/Nonlisted Topic',
                     'Topic :: Scientific/Engineering'],
        test_suite='nose.collector',
        tests_require=['nose'],
        scripts=[os.path.join('scripts', f) for f in os.listdir('scripts')]
    )
