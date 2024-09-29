'''Setup script for lascheck'''

from setuptools import setup

__version__ = '0.1.5'

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering",
    "Topic :: System :: Filesystems",
    "Topic :: Scientific/Engineering :: Information Analysis",
    ]


setup(name='lascheck',
      version='0.1.5',
      description="checking conformity of Log ASCII Standard (LAS) files to LAS 2.0 standard",
      long_description=open("README.md", "r").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/MandarJKulkarni/lascheck",
      author="Mandar J Kulkarni.",
      author_email="mjkool@gmail.com",
      license="MIT",
      classifiers=CLASSIFIERS,
      keywords="las geophysics version",
      packages=["lascheck", ]
      # entry_points={
      #     'console_scripts': [
      #         'lascheck = lascheck:version'
      #     ],
      # }
      )
