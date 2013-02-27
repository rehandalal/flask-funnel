from __future__ import with_statement

import os
import subprocess
import time

from flask import url_for
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
        app.config.setdefault('BUNDLES_DIR', 'bundles')

        app.config.setdefault('CSS_BUNDLES', {})
        app.config.setdefault('JS_BUNDLES', {})

        @app.context_processor
        def context_processor():
            def get_path(item):
                return os.path.join(app.static_folder, item)

            def get_url(item):
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
                except OSError:
                    if OSError.errno != OSError.errno.EEXIST:
                        raise

            def compile_less(item):
                path_css = get_path('%s.css' % item)
                path_less = get_path(item)

                updated_less = os.path.getmtime(get_path(item))
                updated_css = 0
                if os.path.exists(path_css):
                    updated_css = os.path.getmtime(path_css)

                if updated_less > updated_css:
                    ensure_path_exists(os.path.dirname(path_css))
                    with open(path_css, 'w') as output:
                        subprocess.Popen([app.config.get('LESS_BIN', 'lessc'),
                                          path_less], stdout=output)

                return path_css

            def js(bundle, defer=False, async=False, debug=app.debug):
                if debug:
                    items = ['%s?build=%s' % (item, get_mtime(item)) for item in
                             app.config.get('JS_BUNDLES')[bundle]]
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
                    items = []
                    for item in app.config.get('CSS_BUNDLES')[bundle]:
                        if (item.endswith('.less') and
                            app.config.get('LESS_PREPROCESS')):
                            item = compile_less(item)
                        items.append(item)

                    # Add timestamp to avoid caching.
                    items = ['%s?build=%s' % (item, get_mtime(item))
                             for item in items]
                else:
                    bundle_file = os.path.join(app.config.get('BUNDLES_DIR'),
                                               'css', '%s-min.css' % bundle)
                    items = ('%s?build=%s' % (bundle_file,
                                              get_mtime(bundle_file),),)

                return build_html(items,
                    '<link rel="stylesheet" media="%s" href="%%s" />' % media)

            return dict(js=js, css=css)
