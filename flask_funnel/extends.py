from __future__ import with_statement

import os
import subprocess

from flask import current_app

mapping = []


def extend(accept, export):
    def _wrapper(func):
        mapping.append((accept, export, func))
        return func
    return _wrapper


@extend(accept=".css", export=".css")
@extend(accept=".js", export=".js")
def base(sin, sout, **kw):
    # if you want use the sourcemap
    # you could use `scss --sourcemap` of `coffee -m` to 
    # generate the target script file that include the source map tag
    subprocess.call(["cp", sin, sout])


@extend(accept=".coffee", export=".js")
def coffee(sin, sout, **kw):
    subprocess.call([current_app.config.get("COFFEE_BIN", "coffee"), "-c", "-o", sout, sin])


@extend(accept=".less", export=".css")
def less(sin, sout, **kw):
    subprocess.call([current_app.config.get("LESS_BIN", "lessc"), sin, sout])


@extend(accept=".scss", export=".css")
def scss(sin, sout, **kw):
    subprocess.call([current_app.config.get("SCSS_BIN", "scss"), "--sourcemap", sin, sout])

def produce(filepath, relate_filepath=None):
    """ return processed filepath """
    name, postfix = os.path.splitext(filepath)
    if relate_filepath is None:
        # optional relate_filepath
        relate_filedir = os.path.join(current_app.static_folder,
                                      current_app.config.get('BUNDLES_DIR'),
                                      "tmp")
        if not os.path.exists(relate_filedir):
            os.makedirs(relate_filedir)
        relate_filepath = os.path.join(relate_filedir, name)
    else:
        # remove the postfix
        relate_filepath, _ = os.path.splitext(relate_filepath)

    for accept, export, func in mapping:
        if accept == postfix:
            relate_filepath = relate_filepath + export
            source_path = os.path.join(current_app.static_folder, filepath)
            target_path = os.path.join(current_app.static_folder,
                                       relate_filepath)
            if source_path == target_path:
                # ignore the rewrite original file
                return relate_filepath
            directory_path = os.path.dirname(target_path)
            if not os.path.exists(source_path):
                # if you want ignore it
                #continue
                return relate_filepath
            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))

            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            func(source_path, target_path)
            return relate_filepath

    raise NotImplementedError("did not support the file type of %s" % filepath)
