#!/usr/bin/env python3
#
#

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run mads with python3")
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

setup(
    name='evrm',
    version='25',
    url='https://bitbucket.org/thatebart/evrm',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="En dat schadelijk karakter verzwijgende !!".upper(),
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib",],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''
    
Het bewijs dat deze stoffen gif zijn is te vinden is de :ref:`Material Safety Data Sheet <sds>`, daar staan LD50 waardes in. 

De bedoeling van deze tests zijn om de giftigheid van een stof te bepalen in het geval dat de medicijnen getransporteerd moeten worden. Voor als er een pallet Zyprexa in de fik vliegt tijdens transport bijvoorbeeld.

LD50 staat voor lethal dose 50%, de dosis die nodig is om de helft van de test populatie te vermoorden door toediening van de betreffende st

In het getoonde geval van clozapine is de LD50 251mg/kg en kan men clozapine dus moderately toxic noemen.

Op de Hodge and Sterner Scale:

| 1 Extremely Toxic             1 or less mg/kg
| 2 Highly Toxic                1-50
| 3 Moderately Toxic            50-500
| 4 Slightly Toxic              500-5000
| 5 Practically Non-toxic       5000-15,000
| 6 Relatively Harmless         15,000 or more


''',
   data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(j("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(j("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(j("docs", "_templates")))
              ],
   package_data={'': ["*.crt"],
                 },
   classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
