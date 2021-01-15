# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='mediaprobe',  # Required
    version='0.0.1',  # Required
    description='A wrapper for the Mediainfo CLI tool.',  # Optional
    # long_description=long_description,  # Optional
    # long_description_content_type='text/markdown',  # Optional (see note above)
    author='Eman',  # Optional
    author_email='eacosta@roundabout.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Media Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=['mediaprobe'],  # Required
    python_requires='>=3.6, <4',
    install_requires=[],  # Optional
    include_package_data=True,
    # package_data = {
    #     '': ['readme.md'],
    #     'bin': ['mediainfo.exe']
    # }
)