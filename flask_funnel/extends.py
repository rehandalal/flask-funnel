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
    sout.write(sin.read())


@extend(accept=".coffee", export=".js")
def coffee(sin, sout, **kw):
    ##TODO append mapping tag
    subprocess.call(
        [current_app.config.get("COFFEE_BIN", "coffee"), "-s", "-c"],
        stdin=sin, stdout=sout)


@extend(accept=".less", export=".css")
def less(sin, sout, **kw):
    subprocess.call([current_app.config.get("LESS_BIN", "lessc"), "-"],
                    stdin=sin, stdout=sout)


@extend(accept=".scss", export=".css")
def scss(sin, sout, **kw):
    subprocess.call([current_app.config.get("SCSS_BIN", "scss"), "-s"],
                    stdin=sin, stdout=sout)


def produce(filepath, relate_filepath=None):
    """ return processed filepath """
    name, postfix = os.path.splitext(filepath)
    if relate_filepath is None:
        # optional relate_filepath
        relate_filepath = os.path.join(current_app.config.get('BUNDLES_DIR'),
                                       "tmp", name)
    else:
        # remove the postfix
        relate_filepath, _ = os.path.splitext(relate_filepath)

    for accept, export, func in mapping:
        #print repr((accept, postfix, accept == postfix, accept is postfix))
        if accept == postfix:
            relate_filepath = relate_filepath + export
            source_path = os.path.join(current_app.static_folder, filepath)
            target_path = os.path.join(current_app.static_folder,
                                       relate_filepath)
            directory_path = os.path.dirname(target_path)
            if not os.path.exists(source_path):
                # if you want ignore it
                #continue
                return relate_filepath
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            with open(source_path) as rf:
                with open(target_path, "w") as wf:
                    func(rf, wf)
            return relate_filepath

    raise NotImplementedError("did not support the file type of %s" % filepath)
