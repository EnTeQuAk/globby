#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Globby Bootstrap Creation Script
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Creates a bootstrap script for globby.

    :copyright: Copyright 2008 by Christopher grebs
    :license: GNU GPL.
"""

import sys, os, subprocess

import virtualenv

EXTRA_TEXT = """
def easy_install(package, home_dir, optional_args=None):
    optional_args = optional_args or []
    cmd = [os.path.join(home_dir, 'bin', 'easy_install')]
    cmd.extend(optional_args)
    cmd.append(package)
    call_subprocess(cmd)


def after_install(options, home_dir):
    easy_install('Jinja2', home_dir)
    easy_install('Pygments', home_dir)
    #easy_install('DMLT', home_dir)
"""

def main():
    if len(sys.argv) == 2:
        print virtualenv.create_bootstrap_script(EXTRA_TEXT, python_version=sys.argv[1])
    else:
        print >>sys.stderr, "Specify the python version you want to use as"\
                            " first parameter (eg. 2.4)"

if __name__ == '__main__':
    main()
