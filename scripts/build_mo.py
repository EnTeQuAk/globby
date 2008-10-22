#!/usr/bin/env python

import optparse
import os
from os.path import join, pardir, dirname
import sys

def compile_messages(basedir):
    for dirpath, dirnames, filenames in os.walk(basedir):
        for f in filenames:
            if f.endswith('.po'):
                sys.stderr.write('processing file %s in %s\n' % (f, dirpath))
                pf = os.path.splitext(os.path.join(dirpath, f))[0]
                # Store the names of the .mo and .po files in an environment
                # variable, rather than doing a string replacement into the
                # command, so that we can take advantage of shell quoting, to
                # quote any malicious characters/escaping.
                # See http://cyberelk.net/tim/articles/cmdline/ar01s02.html
                os.environ['globbycompilemo'] = pf + '.mo'
                os.environ['globbycompilepo'] = pf + '.po'
                if sys.platform == 'win32': # Different shell-variable syntax
                    cmd = 'msgfmt --check-format -o "%globbyompilemo%" "%globbycompilepo%"'
                else:
                    cmd = 'msgfmt --check-format -o "$globbycompilemo" "$globbycompilepo"'
                os.system(cmd)

def main():
    pth = join(dirname(__file__), pardir, 'globby', 'cli', 'locale')
    compile_messages(pth)

if __name__ == "__main__":
    main()
