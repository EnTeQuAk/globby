#!/usr/bin/env python

import re
import os
from os.path import join, abspath, pardir, isdir, dirname
import sys
import getopt
pythonize_re = re.compile(r'\n\s*//')

def make_messages():
    localedir = None

    if isdir('locale'):
        localedir = abspath('locale')
    elif isdir(join('globby', 'cli', 'locale')):
        localedir = abspath(join('globby', 'cli', 'locale'))
    elif isdir(join(abspath(dirname(__file__)), pardir, 'globby', 'cli', 'locale')):
        localedir = join(abspath(dirname(__file__)), pardir, 'globby', 'cli', 'locale')
    else:
        print "You must run this script from the 'scripts' directory in the globby"
        print "root tree. Else it doesn't find the locales"
        sys.exit(1)
    (opts, args) = getopt.getopt(sys.argv[1:], 'l:d:va')

    lang = None
    domain = 'globby'
    verbose = False
    all = False

    for o, v in opts:
        if o == '-l':
            lang = v
        elif o == '-d':
            domain = v
        elif o == '-v':
            verbose = True
        elif o == '-a':
            all = True

    if domain not in ('globby',):
        print "currently make-messages.py only supports only the domain 'globby'"
        sys.exit(1)
    if (lang is None and not all) or domain is None:
        print "usage: build_gettext.py -l <language>"
        print "   or: build_gettext.py -a"
        sys.exit(1)

    languages = []

    if lang is not None:
        languages.append(lang)
    elif all:
        languages = [el for el in os.listdir(localedir) if not el.startswith('.')]

    for lang in languages:

        print "processing language", lang
        basedir = os.path.join(localedir, lang, 'LC_MESSAGES')
        if not os.path.isdir(basedir):
            os.makedirs(basedir)

        pofile = os.path.join(basedir, '%s.po' % domain)
        potfile = os.path.join(basedir, '%s.pot' % domain)

        if os.path.exists(potfile):
            os.unlink(potfile)

        for (dirpath, dirnames, filenames) in os.walk("."):
            if dirpath.startswith('./globby') or 'globby.py' in filenames:
                for file in filenames:
                    if domain == 'globby' and file.endswith('.py'):
                        thefile = file
                        if verbose: sys.stdout.write('processing file %s in %s\n' % (file, dirpath))
                        cmd = 'xgettext %s -d %s -L Python --keyword=_ --keyword=N_ --from-code UTF-8 -o - "%s"' % (
                            os.path.exists(potfile) and '--omit-header' or '', domain, os.path.join(dirpath, thefile))
                        (stdin, stdout, stderr) = os.popen3(cmd, 'b')
                        msgs = stdout.read()
                        errors = stderr.read()
                        if errors:
                            print "errors happened while running xgettext on %s" % file
                            print errors
                            sys.exit(8)
                        if thefile != file:
                            old = '#: '+os.path.join(dirpath, thefile)[2:]
                            new = '#: '+os.path.join(dirpath, file)[2:]
                            msgs = msgs.replace(old, new)
                        if msgs:
                            open(potfile, 'ab').write(msgs)
                        if thefile != file:
                            os.unlink(os.path.join(dirpath, thefile))

        if os.path.exists(potfile):
            (stdin, stdout, stderr) = os.popen3('msguniq "%s"' % potfile, 'b')
            msgs = stdout.read()
            errors = stderr.read()
            if errors:
                print "errors happened while running msguniq"
                print errors
                sys.exit(8)
            open(potfile, 'w').write(msgs)
            if os.path.exists(pofile):
                (stdin, stdout, stderr) = os.popen3('msgmerge -q "%s" "%s"' % (pofile, potfile), 'b')
                msgs = stdout.read()
                errors = stderr.read()
                if errors:
                    print "errors happened while running msgmerge"
                    print errors
                    sys.exit(8)
            open(pofile, 'wb').write(msgs)
            os.unlink(potfile)
        #XXX: convert the datafiles to utf-8, because they're saved in iso-8859-1
        po_data = read_file(pofile)
        write_file(pofile, po_data)


def read_file(filename, charset='utf-8'):
    f = open(filename, 'rb')
    try:
        data = to_unicode(
            re.sub(r'\r\n|\r|\n', '\n', f.read()),
            charset)
    finally:
        f.close()
    return data


def write_file(filename, data, charset='utf-8'):
    f = open(filename, 'w')
    if not isinstance(data, unicode):
        # wtf? -- if this happens... I kill myself ;)
        data = to_unicode(data)
    try:
        f.write(data.encode(charset))
    finally:
        f.close()


def to_unicode(text, charset=None):
    if isinstance(text, unicode):
        # the string isn't a 'str' instance... then it is a 'unicode' one
        return text
    if charset:
        # try to decode with the given 'charset'
        return text.decode(charset, 'replace')
    else:
        try:
            # decode with 'charset' doesn't work... try 'utf-8'
            return text.decode('utf-8')
        except UnicodeError:
            try:
                # 'utf-8' still not work? -- try the local preferred encoding
                return text.decode(locale.getpreferredencoding(), 'replace')
            except UnicodeError:
                # it nothing work... fallback to 'iso-8859-15'
                return text.decode('iso-8859-15', 'replace')




if __name__ == "__main__":
    make_messages()
