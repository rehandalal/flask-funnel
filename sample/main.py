from flask import Flask, render_template
from flask.ext.funnel import Funnel

app = Flask(__name__)
Funnel(app)

app.config['JAVA_BIN'] = '/usr/java/latest/bin/java'

app.config['LESS_PREPROCESS'] = True

app.config['CSS_BUNDLES'] = {
    '1': (
        'css/1.css',
    ),
    '2': (
        'css/2.css',
    ),
    '3': (
        'css/3.css',
    ),
    '1-2': (
        'css/1.css',
        'css/2.css',
    ),
    'less-1': (
        'less/1.less',
    ),
    'less-2': (
        'less/2.less',
    ),
    'less-2-3': (
        'less/2.less',
        'less/3.less',
    ),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/example1')
def example1():
    """Debug enabled, basic template functions"""
    app.config['DEBUG'] = True
    return render_template('example1.html')

@app.route('/example2')
def example2():
    """Debug enabled, LESS files"""
    app.config['DEBUG'] = True
    return render_template('example2.html')
