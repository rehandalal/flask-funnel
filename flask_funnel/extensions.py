from __future__ import with_statement, absolute_import

import os
import subprocess

from flask import current_app


preprocessors = []
postprocessors = []


def preprocessor(accepts, exports, flag=None):
    """Decorator to add a new preprocessor"""
    def decorator(f):
        preprocessors.append((accepts, exports, flag, f))
        return f
    return decorator


def postprocessor(accepts, flag=None):
    """Decorator to add a new postprocessor"""
    def decorator(f):
        postprocessors.append((accepts, flag, f))
        return f
    return decorator


@preprocessor(accepts='.coffee', exports='.js', flag='COFFEE_PREPROCESS')
def coffee(input, output, **kw):
    """Process CoffeeScript files"""
    subprocess.call([current_app.config.get('COFFEE_BIN'),
                     '-c', '-o', output, input])


@preprocessor(accepts='.less', exports='.css', flag='LESS_PREPROCESS')
def less(input, output, **kw):
    """Process LESS files"""
    subprocess.call([current_app.config.get('LESS_BIN'), input, output])


@preprocessor(accepts='.scss', exports='.css', flag='SCSS_PREPROCESS')
def scss(input, output, **kw):
    """Process SASS files"""
    subprocess.call([current_app.config.get('SCSS_BIN'),
                     '--sourcemap', input, output])


@preprocessor(accepts='.styl', exports='.css', flag='STYLUS_PREPROCESS')
def stylus(input, output, **kw):
    """Process Stylus (.styl) files"""
    stdin = open(input, 'r')
    stdout = open(output, 'w')
    cmd = '%s --include %s' % (current_app.config.get('STYLUS_BIN'),
                               os.path.abspath(os.path.dirname(input)))
    subprocess.call(cmd, shell=True, stdin=stdin, stdout=stdout)


@postprocessor('.css', 'AUTOPREFIXER_ENABLED')
def autoprefixer(input, **kw):
    """Run autoprefixer"""
    cmd = '%s -b "%s" %s' % (current_app.config.get('AUTOPREFIXER_BIN'),
                             current_app.config.get('AUTOPREFIXER_BROWSERS'),
                             input)
    subprocess.call(cmd, shell=True)


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
                except OSError as e:
                    if e.errno != os.errno.EEXIST:
                        raise

                func(source, target)
                postprocess(target)
            return target_name
    return filename


def postprocess(filename, fix_path=False):
    for accepts, flag, func in postprocessors:
        if (filename.endswith(accepts) and
                (not flag or current_app.config.get(flag))):
            source = (filename if not fix_path else
                      os.path.join(current_app.static_folder, filename))
            func(source)
    return filename
