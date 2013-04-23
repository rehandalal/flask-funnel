from __future__ import with_statement

import math
import os
import subprocess
import time

from jinja2 import Markup

class Funnel(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app

        app.config.setdefault('CSS_MEDIA_DEFAULT', 'screen,projection,tv')
        app.config.setdefault('LESS_PREPROCESS', False)
        app.config.setdefault('SCSS_PREPROCESS', False)
        app.config.setdefault('COFFEE_PREPROCESS', False)
        app.config.setdefault('BUNDLES_DIR', 'bundles')
        app.config.setdefault('FUNNEL_USE_S3', False)

        app.config.setdefault('CSS_BUNDLES', {})
        app.config.setdefault('JS_BUNDLES', {})

        processer_map = {
            '.less': (app.config.get('LESS_BIN', 'lessc'), '.css', 'LESS_PREPROCESS'),
            '.scss': (app.config.get('SCSS_BIN', 'scss'), '.css', 'SCSS_PREPROCESS'),
            'offee': (app.config.get('COFFEE_BIN', 'coffee'), '.js', 'COFFEE_PREPROCESS'),
        }

        def get_path(item):
            return os.path.join(app.static_folder, item)

        tmp_dir = get_path(os.path.join(self.app.config.get('BUNDLES_DIR'), 'tmp'))

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        @app.context_processor
        def context_processor():
            def get_url(item):
                if app.config.get('FUNNEL_USE_S3'):
                    try:
                        from flask.ext.s3 import url_for
                    except ImportError:
                        from flask import url_for
                else:
                    from flask import url_for
                if item.startswith(('//', 'http://', 'https://')):
                    return item
                item = item.split('?', 1)
                url = url_for('static', filename=item[0])
                if item[1]:
                    url += '?' + item[1]
                return url

            def get_mtime(item):
                if item.startswith(('//', 'http://', 'https://')):
                    return int(time.time())

                try:
                    return int(os.path.getmtime(get_path(item)))
                except OSError:
                    return int(time.time())

            def build_html(items, wrapper):
                return Markup('\n'.join((wrapper % (get_url(item))
                    for item in items)))

            def ensure_path_exists(path):
                try:
                    os.makedirs(path)
                except OSError, e:
                    if e.errno != os.errno.EEXIST:
                        raise

            def precompile(processer_bin, postfix, item):
                filename = os.path.join(self.app.config.get('BUNDLES_DIR'), 'tmp', item + postfix)
                target_path = get_path(filename)
                source_path = get_path(item)

                preupdated = os.path.getmtime(get_path(item))
                updated = 0
                if os.path.exists(target_path):
                    updated = os.path.getmtime(target_path)

                if preupdated > updated:
                    ensure_path_exists(os.path.dirname(target_path))
                    with open(target_path, 'w') as output:
                        #TODO use popen.wait to void the time.sleep
                        if postfix == '.js':
                            # deal with coffee
                            with open(source_path, 'r') as stdin:
                                subprocess.Popen([processer_bin, '-s', '-c'], stdout=output, stdin=stdin)
                        else:
                            subprocess.Popen([processer_bin, source_path], stdout=output)

                return filename

            def _build(bundle_tp, bundle):
                precompiling = 0
                items = []
                for item in app.config.get(bundle_tp)[bundle]:
                    processer_bin, postfix, condition = processer_map.get(item[-5:], (None, None, None))
                    if app.config.get(condition):                            
                        precompiling += 1
                        item = precompile(processer_bin, postfix, item)
                    items.append(item)

                # Add timestamp to avoid caching.
                items = ['%s?build=%s' % (item, get_mtime(item))
                         for item in items]

                # Sleep to allow precompile files to fully compile
                if precompiling > 0:
                    time.sleep(math.ceil(precompiling / 4) * 1)
                return items

            def js(bundle, defer=False, async=False, debug=app.debug):
                if debug:
                    items = _build('JS_BUNDLES', bundle)
                else:
                    bundle_file = os.path.join(app.config.get('BUNDLES_DIR'),
                                               'js', '%s-min.js' % bundle)
                    items = ('%s?build=%s' % (bundle_file,
                                              get_mtime(bundle_file)),)

                attrs = ['src="%s"']

                if defer:
                    attrs.append('defer')

                if async:
                    attrs.append('async')

                string = '<script %s></script>' % ' '.join(attrs)
                return build_html(items, string)

            def css(bundle, media=None, debug=app.debug):
                if media is None:
                    media = app.config.get('CSS_MEDIA_DEFAULT')

                if debug:
                    items = _build('CSS_BUNDLES', bundle)
                else:
                    bundle_file = os.path.join(app.config.get('BUNDLES_DIR'),
                                               'css', '%s-min.css' % bundle)
                    items = ('%s?build=%s' % (bundle_file,
                                              get_mtime(bundle_file),),)

                return build_html(items,
                                  '<link rel="stylesheet" media="%s" href="%%s" />' % media)

            return dict(js=js, css=css)
