# -*- coding: utf-8 -*-

from distutils.core import setup

from ivctrack import __version__

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ivctrack',
    packages=['ivctrack'],
    package_data={'ivctrack': ['c-code/*']},
    version=__version__,
    description='2D in-vitro cell tracking',
    author='Olivier Debeir',
    author_email='odebeir@ulb.ac.be',
    url='https://odebeir@bitbucket.org/odebeir/icvtrack.git',
    keywords = ["image processing", "tracking", "numpy"],

    classifiers = [
            "Programming Language :: Python",
            "Programming Language :: C",
            "Development Status :: 4 - Beta",
            "Environment :: Other Environment",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering :: Image Recognition",
            "Topic :: Software Development :: Libraries",
            ],

    long_description=readme,
    license=license,

)
