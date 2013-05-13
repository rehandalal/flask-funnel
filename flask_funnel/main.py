from __future__ import with_statement

import math
import os
import subprocess
import time

from jinja2 import Markup

from extends import produce


class Funnel(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app

        app.config.setdefault('CSS_MEDIA_DEFAULT', 'screen,projection,tv')
        app.config.setdefault('BUNDLES_DIR', 'bundles')
        app.config.setdefault('FUNNEL_USE_S3', False)

        app.config.setdefault('CSS_BUNDLES', {})
        app.config.setdefault('JS_BUNDLES', {})

        def get_path(item):
            return os.path.join(app.static_folder, item)

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

            def _build(bundle_tp, bundle):
                items = []
                for item in app.config.get(bundle_tp)[bundle]:
                    items.append(produce(item))

                # Add timestamp to avoid caching.
                items = ['%s?build=%s' % (item, get_mtime(item))
                         for item in items]

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

                ss_html = '<link rel="stylesheet" media="%s" href="%%s" />'
                return build_html(items, ss_html % media)

            return dict(js=js, css=css)
