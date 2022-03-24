# Always prefer setuptools over distutils
from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='mediaprobe',
    version='1.0.0',
    description='A wrapper for the Mediainfo CLI tool.',
    author='Eman',
    author_email='eacosta@roundabout.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Media Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=['mediaprobe'],
    python_requires='>=3.6, <4',
    install_requires=[],
    include_package_data=True,
)