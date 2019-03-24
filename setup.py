__version__ = "0.2.1"

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyaltt",
    version=__version__,
    author='Altertech Group',
    author_email="pr@altertech.com",
    description="Various tools for functions, looped and queued workers etc.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/alttch/pyaltt",
    packages=setuptools.find_packages(),
    license='Apache License 2.0',
    install_requires=[],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ),
)
