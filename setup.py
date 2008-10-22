# -*- coding: utf-8 -*-
import os
import globby
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
from inspect import getdoc


def list_files(path):
    for fn in os.listdir(path):
        if fn.startswith('.'):
            continue
        fn = os.path.join(path, fn)
        if os.path.isfile(fn):
            yield fn

setup(
    name = 'Globby',
    version = '0.2',
    url = 'http://globby.webshox.org/',
    license = 'GNU GPL',
    author = 'Sebastian Koch',
    author_email = 'mr-snede@web.de',
    description = ('A small and easy to use stand-alone website generator'),
    long_description = getdoc(globby),
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = ['python.web.website'],
    packages = ['globby'],
    #data_files = [
    #    ('docs', list(list_files('docs'))),
    #],
    platforms = 'any',
    extras_require = {'plugin': ['setuptools>=0.6a2']},
)
