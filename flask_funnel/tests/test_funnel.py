import unittest

from flask import Flask, render_template_string
from flask.ext.funnel import Funnel

class FunnelTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        Funnel(app)

        app.config['CSS_BUNDLES'] = {
                'css-bundle': (
                    'css/test.css',
                    'less/test.less',
                ),
            }

        app.config['JS_BUNDLES'] = {
                'js-bundle': (
                    'js/test1.js',
                    'js/test2.js',
                ),
            }

        @app.route('/')
        def index():
            return render_template_string(
                "{{ css('css-bundle') }} {{ js('js-bundle') }}")

        self.app = app
        self.client = app.test_client()

    def test_css_helper_function(self):
        """Test the css() helper function"""
        data = self.client.get('/').data
        assert '/static/bundles/css/css-bundle-min.css' in data

        self.app.config['DEBUG'] = True
        data = self.client.get('/').data
        assert '/static/css/test.css' in data
        assert '/static/less/test.less' in data

    def test_js_helper_function(self):
        """Test the js() helper function"""
        data = self.client.get('/').data
        assert '/static/bundles/js/js-bundle-min.js' in data

        self.app.config['DEBUG'] = True
        data = self.client.get('/').data
        assert '/static/js/test1.js' in data
        assert '/static/js/test2.js' in data
