from __future__ import with_statement

import os
import subprocess

from flask import current_app

mapping = []


def extend(accept, export, preprocess_setting=None):
    def _wrapper(func):
        mapping.append((accept, export, preprocess_setting, func))
        return func
    return _wrapper


@extend(accept='.coffee', export='.js',
        preprocess_setting='COFFEE_PREPROCESS')
def coffee(sin, sout, **kw):
    subprocess.call([current_app.config.get('COFFEE_BIN', 'coffee'),
                     '-c', '-o', sout, sin])


@extend(accept='.less', export='.css',
        preprocess_setting='LESS_PREPROCESS')
def less(sin, sout, **kw):
    subprocess.call([current_app.config.get('LESS_BIN', 'lessc'), sin, sout])


@extend(accept='.scss', export='.css',
        preprocess_setting='SCSS_PREPROCESS')
def scss(sin, sout, **kw):
    subprocess.call([current_app.config.get('SCSS_BIN', 'scss'),
                     '--sourcemap', sin, sout])


@extend(accept='.styl', export='.css',
        preprocess_setting='STYLUS_PREPROCESS')
def stylus(input, output):
    stdin = open(input, 'r')
    stdout = open(output, 'w')
    subprocess.call([current_app.config.get('STYLUS_BIN', 'stylus')],
                    stdin=stdin, stdout=stdout)


def preprocess(filename):
    for accept, export, preprocess_setting, func in mapping:
        if (filename.endswith(accept) and
                current_app.config.get(preprocess_setting)):
            target_name = '%s%s' % (filename, export)

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
