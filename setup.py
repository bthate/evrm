#!/usr/bin/env python3
# This file is placed in the Public Domain.


import os


from setuptools import setup


def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl


def read():
    return open("README.rst", "r").read()


setup(
    name='evrm',
    version='111',
    url='https://github.com/bthate/evrm',
    author='Bart Thate',
    author_email='bthate67@gmail.com',
    description="@KarimKhanQC reconsider OTP-CR-117/19",
    license='Public Domain',
    zip_safe=False,
    scripts=["bin/evrm"],
    long_description=read(),
    packages=["evrm"],
    include_package_data=True,
    data_files=[("share/doc/evrm", uploadlist("docs"))],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Public Domain',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
