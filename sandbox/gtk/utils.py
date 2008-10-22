#-*- coding: utf-8 -*-

from os.path import join, dirname, abspath
import re
import pango

__all__ = ['main_path', 'get_copyright', 'VERSION',
           'AUTHORS', 'TRANSLATORS', 'LICENSE']

#only for development in the sandbox
main_path = '/'.join(abspath(dirname(__file__)).split('/')[:-2])

def get_copyright():
    """Return the copyright string for the about dialog."""
    import globby
    return 'Copyright %s' % re.compile(r'^\s+:%s:\s+(.*?)\.$(?m)' % 'copyright') \
            .search(globby.__doc__).group(1).strip()

def _get_lines(filename, strip=False):
    result = []
    f = file(join(main_path, filename))
    try:
        for line in f:
            line = strip and line.strip() or line
            if line and not line.startswith('#'):
                result.append(line)
    finally:
        f.close()
    return result


VERSION = (0, 1)
AUTHORS = _get_lines('AUTHORS', True)
TRANSLATORS = _get_lines('TRANSLATORS', True)
LICENSE = ''.join(_get_lines('LICENSE', False))
LICENSE = LICENSE.replace('(see AUTHORS)', '')

# Text Preview
STYLES = {
    'headline1': {
        'scale': pango.SCALE_XX_LARGE,
        'weight': pango.WEIGHT_BOLD,
    },
    'headline2': {
        'scale': pango.SCALE_X_LARGE,
        'weight': pango.WEIGHT_BOLD,
    },
    'headline3': {
        'scale': pango.SCALE_LARGE,
    },
    'headline4': {
        'scale': pango.SCALE_MEDIUM,
    },
    'headline5': {
        'scale': pango.SCALE_SMALL,
    },
    'headline6': {
        'scale': pango.SCALE_X_SMALL,
    },
}
