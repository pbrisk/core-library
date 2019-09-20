# -*- coding: utf-8 -*-

#  corelibrary
#  -----------
#  A core financial risk analytics library.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/corelibrary
#  License: European Union Public Licence 1.1


import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='corelibrary',
    description='A core financial risk analytics library.',
    version='0.1.1',
    author='pbrisk, based on a fork of Deutsche Postbank [pbrisk]',
    author_email='pbrisk_at_github@icloud.com',
    url='https://github.com/pbrisk/corelibrary',
    bugtrack_url='https://github.com/pbrisk/corelibrary/issues',
    license='European Union Public Licence 1.1',
    packages=[
        'corelibrary',
        'corelibrary.base',
        'corelibrary.base.interface',
        'corelibrary.base.namedobject',
        'corelibrary.business',
        'corelibrary.business.index',
        'corelibrary.business.product',
        'corelibrary.analytics',
        'corelibrary.analytics.model',
        'corelibrary.analytics.model.factormodel',
        'corelibrary.analytics.model.indexmodel',
        'corelibrary.analytics.parameter',
        'corelibrary.analytics.parameter.vol',
        'corelibrary.analytics.result',
        'corelibrary.utils',
        'corelibrary.utils.fileutils',
        'corelibrary.utils.maths'],
    install_requires=[
        'unicum==0.2',
        'goma==0.1',
        'mitschreiben==0.2',
        'businessdate==0.4',
        'dcf==0.2',
        'mathtoolspy==0.2',
        'putcall==0.1',
        'timewave==0.5',
        'shortrate==0.2',
        'numpy',
        'scipy',
    ],
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
