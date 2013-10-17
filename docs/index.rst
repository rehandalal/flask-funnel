==============
 Flask-Funnel
==============

.. contents::
   :local:


.. include:: ../README.rst


Requirements
============

* **Flask 0.8** (or later)

One of the following:

* **Java**: if you want to use `YUI Compressor`_.
* **NodeJS**: if you want to use `Coffee-Script`_ , `UglifyJS`_ or `clean-css`_.

Optionally:

* **LESS**: if you need to compile `LESS`_ files.
* **SCSS**: if you need to compile `SCSS`_ files.
* **Stylus**: if you need to compule `Stylus`_ files.
* **COFFEE**: if you need to compile `COFFEE`_ files.


Installing YUI Compressor
=========================

To use `YUI Compressor`_ you must install Java. Once Java has been installed
make sure to set ``JAVA_BIN`` in your application config.

You can download YUI Compressor from
`<https://github.com/yui/yuicompressor/downloads>`_ and make sure that
``YUI_COMPRESSOR_BIN`` points to the ``yuicompressor-x.y.z.jar`` file.


Quickstart
==========

To get started using Flask-Funnel simply add the following to your Flask app::

    from flask import Flask
    from flask.ext.import Funnel

    app = Flask(__name__)
    Funnel(app)


Configuration
=============

There are several configuration options available for **Flask-Funnel**:

**CSS_BUNDLES**

    A dict of CSS bundles:

    .. code-block:: python

        app.config['CSS_BUNDLES'] = {
            'bundle1': (
                'stylesheet.css',
                'another.css',
                'tobecompile.less',
                'tobecompile2.scss',
            ),
        }

    Defaults to: ``{}``

**JS_BUNDLES**

    A dict of JavaScript bundles:

    .. code-block:: python

        app.config['JS_BUNDLES'] = {
            'the_bundle': (
                'jquery.js',
                'jquery-ui.js',
                'tubecompile.coffee',
            ),
        }

    Defaults to: ``{}``

**CSS_MEDIA_DEFAULT**

    This is the default value for the media attribute of the <link> tag for
    stylesheets.

    Defaults to: ``'screen,projection,tv'``

**BUNDLES_DIR**

    The subdirectory of the static directory that the generated bundles are saved
    to.

    Defaults to: ``'bundles'``

**YUI_COMPRESSOR_BIN**

    If you plan on using `YUI Compressor`_ you must set this variable.

    *It has no default value.*

**JAVA_BIN**

    If you plan on using `YUI Compressor`_ you must set this variable.

    *It has no default value.*

**LESS_BIN**

    If you require `LESS`_ support you must point this to ``lessc``.

    Defaults to: ``'lessc'``

**LESS_PREPROCESS**

    If you want LESS files to be compiled when ``app.debug`` is ``True`` and
    compressed files are not being used.

    Defaults to: ``True``

**SCSS_BIN**

    If you require `SCSS`_ support you must point this to ``scss``.

    Defaults to: ``'scss'``

**SCSS_PREPROCESS**

    If you want SCSS files to be compiled when ``app.debug`` is ``True`` and
    compressed files are not being used.

    Defaults to: ``True``

**STYLUS_BIN**

  If you require `Stylus`_ support you must point this to ``stylus``.

  Defaults to: ``'stylus'``

**STYLUS_PREPROCESS**

    If you want Stylus files to be compiled when ``app.debug`` is ``True`` and
    compressed files are not being used.

    Defaults to: ``True``

**COFFEE_BIN**

    If you require `COFFEE`_ support you must point this to ``coffee``.

    Defaults to: ``'coffee'``

**COFFEE_PREPROCESS**

    If you want CoffeeScript files to be compiled when ``app.debug`` is
    ``True`` and compressed files are not being used.

    Defaults to: ``True``

**UGLIFY_BIN**

    If you want to use `UglifyJS`_ you must set this variable.

    *It has no default value.*

**CLEANCSS_BIN**

    If you want to use `clean-css`_ you must set this variable.

    *It has no default value.*

**FUNNEL_USE_S3**

    If you are using `Flask-S3`_ you must set this to use Flask-S3's
    ``url_for()`` function.

    Defaults to: ``False``

Including bundles in templates
==============================

To include a bundle in a template you can use the ``css()``  or ``js()``
function:

.. code-block:: html+jinja

    {# Jinja2 template #}
    <!doctype html>
    <html>
    <head>
        <title>The Title</title>
        {{ css('bundle-name') }}
    </head>
    <body>
        <h1>Headline</h1>
        {{ js('bundle-name') }}
    </body>
    </html>


This will generate the appropriate markup for each bundle.

Note: When ``app.debug`` is ``True`` these will output markup for each file in
the bundle.


Media types for stylesheets
---------------------------

The ``css()`` function will, by default, generate ``<link>`` tags with a
``media`` attribute set to ``CSS_MEDIA_DEFAULT``. You can override this by
passing an optional second argument.


Using the manager to bundle and minify assets
---------------------------------------------

The extension provides a sub-manager for `Flask-Script`_ which can be used as
follows:

.. code-block:: python

    from flask.ext.script import Manager
    from flask.ext.funnel.manager import manager as funnel_manager

    manager = Manager(app)
    manager.add_command('funnel', funnel_manager)


You can now use the manager to bundle and minify your assets using::

    $ ./manage.py funnel bundle_assets


This will create a ``bundle`` folder within the app's static folder to store the
bundled files. CSS bundles go into a ``css`` subfolder and JavaScript bundles go
into the ``js`` subfolder. Each of these subfolders will have a number of
``*-min.*`` files which are the compressed and minified versions of the bundles.


.. include:: ../CHANGELOG


.. include:: ../CONTRIBUTORS


.. _clean-css: http://github.com/GoalSmashers/clean-css
.. _Flask: http://flask.pocoo.org/
.. _Flask-S3: http://github.com/e-dard/flask-s3
.. _Flask-Script: http://github.com/techniq/flask-script
.. _GitHub: http://github.com/rehandalal/flask-funnel
.. _LESS: http://lesscss.org/
.. _UglifyJS: http://github.com/mishoo/UglifyJS
.. _YUI Compressor: http://github.com/yui/yuicompressor
.. _COFFEE: http://jashkenas.github.com/coffee-script/
.. _SCSS: http://sass-lang.com/
.. _Stylus: http://learnboost.github.io/stylus/
