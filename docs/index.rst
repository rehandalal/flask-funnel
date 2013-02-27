Flask-Funnel
============

The **Flask-Funnel** extension provides support for bundling and minification of
assets for `Flask`_.


Requirements
------------

* **Flask 0.8** (or later)

One of the following:

* **Java**: if you want to use `YUI Compressor`_.
* **NodeJS**: if you want to use `UglifyJS`_ or `clean-css`_.

Optionally:

* **LESS**: if you need to compile `LESS`_ files.


Configuration
-------------

There are several configuration options available for **Flask-Funnel**:

**CSS_BUNDLES**

A dict of CSS bundles::

    app.config['CSS_BUNDLES'] = {
        'bundle1': (
            'stylesheet.css',
            'another.css',
        ),
    }

*Default:* ``{}``

**JS_BUNDLES**

A dict of JavaScript bundles::

    app.config['JS_BUNDLES'] = {
        'the_bundle': (
            'jquery.js',
            'jquery-ui.js',
        ),
    }

*Default:* ``{}``

**CSS_MEDIA_DEFAULT**

*Default:* ``'screen,projection,tv'``

**BUNDLES_DIR**

The subdirectory of the static directory that the generated bundles are saved
to.

*Default:* ``'bundles'``

**JAVA_BIN**

If you plan on using `YUI Compressor`_ you must set this variable.

*It has no default value.*

**LESS_BIN**

If you require `LESS`_ support you must point this to ``lessc``.

*Default:* ``'lessc'``

**LESS_PREPROCESS**

If you want LESS files to be compiled when ``app.debug`` is ``True`` and
compressed files are not being used.

*Default:* ``True``

**UGLIFY_BIN**

If you want to use `UglifyJS`_ you must set this variable.

*It has no default value.*

**CLEANCSS_BIN**

If you want to use `clean-css`_ you must set this variable.

*It has no default value.*


Including bundles in templates
------------------------------

To include a bundle in a template you can use the ``css()``  or ``js()``
function::

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
...........................

The ``css()`` function will, by default, generate ``<link>`` tags with a
``media`` attribute set to ``CSS_MEDIA_DEFAULT``. You can override this by
passing an optional second argument.


Using the manager to bundle and minify assets
---------------------------------------------

The extension provides a sub-manager for `Flask-Script`_ which can be used as
follows::

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


.. _clean-css: http://github.com/GoalSmashers/clean-css
.. _Flask: http://flask.pocoo.org/
.. _Flask-Script: http://github.com/techniq/flask-script
.. _GitHub: http://github.com/rehandalal/flask-funnel
.. _LESS: http://lesscss.org/
.. _UglifyJS: http://github.com/mishoo/UglifyJS
.. _YUI Compressor: http://github.com/yui/yuicompressor