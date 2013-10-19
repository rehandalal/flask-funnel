from __future__ import with_statement

import os
import subprocess

from flask import current_app

preprocessors = []


def add_preprocessor(accepts, exports, flag=None):
    def _wrapper(func):
        preprocessors.append((accepts, exports, flag, func))
        return func
    return _wrapper


@add_preprocessor(accepts='.coffee', exports='.js', flag='COFFEE_PREPROCESS')
def coffee(input, output, **kw):
    subprocess.call([current_app.config.get('COFFEE_BIN'),
                     '-c', '-o', output, input])


@add_preprocessor(accepts='.less', exports='.css', flag='LESS_PREPROCESS')
def less(input, output, **kw):
    subprocess.call([current_app.config.get('LESS_BIN'), input, output])


@add_preprocessor(accepts='.scss', exports='.css', flag='SCSS_PREPROCESS')
def scss(input, output, **kw):
    subprocess.call([current_app.config.get('SCSS_BIN'),
                     '--sourcemap', input, output])


@add_preprocessor(accepts='.styl', exports='.css', flag='STYLUS_PREPROCESS')
def stylus(input, output):
    stdin = open(input, 'r')
    stdout = open(output, 'w')
    subprocess.call([current_app.config.get('STYLUS_BIN')],
                    stdin=stdin, stdout=stdout)


def preprocess(filename):
    for accepts, exports, flag, func in preprocessors:
        if (filename.endswith(accepts) and
                (not flag or current_app.config.get(flag))):
            target_name = '%s%s' % (filename, exports)

            source = os.path.join(current_app.static_folder, filename)
            target = os.path.join(current_app.static_folder, target_name)

            source_mtime = os.path.getmtime(source)
            target_mtime = 0
            if os.path.exists(target):
                target_mtime = os.path.getmtime(target)

            if source_mtime > target_mtime:
                try:
                    os.makedirs(os.path.dirname(target))
                except OSError, e:
                    if e.errno != os.errno.EEXIST:
                        raise

                func(source, target)

            return target_name
    return filename
