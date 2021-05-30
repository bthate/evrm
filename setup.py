#!/usr/bin/env python3
# EVRM - ANTIPSYCHOTICA - AKATHISIA - KATATONIE - SEDERING - SHOCKS - LETHALE KATATONIE !!!
#
# this file is in the Public Domain

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run evrm with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

target = "evrm"
upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir):
        print("%s does not exist" % dir)
        os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl

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
    version='72',
    url='https://github.com/bthate/evrm',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="ANTIPSYCHOTICA - AKATHISIA - KATATONIE - SEDERING - SHOCKS - LETHALE KATATONIE !!!",
    license='Public Domain',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    long_description=read(),
    data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(j("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(j("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(j("docs", "_templates")))
              ],
    package_data={'': ["*.crt"],
                 },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Public Domain',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
