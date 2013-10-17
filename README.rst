Summary
=======

A Flask extension for compressing/minifying assets.

A Flask-Script submanager is also provided.

.. image:: https://api.travis-ci.org/rehandalal/flask-funnel.png


Documentation
=============

Documentation is at
`<http://flask-funnel.readthedocs.org/en/latest/>`_.


Install
=======

To install::

    $ pip install Flask-Funnel


You can also install the development version
`<https://github.com/rehandalal/flask-funnel/tarball/master#egg=Flask-Funnel-dev>`_::

    $ pip install Flask-Funnel==dev


or::

    $ git clone git://github.com/rehandalal/flask-funnel.git
    $ mkvirtualenv flaskfunnel
    $ python setup.py develop
    $ pip install -r requirements.txt


Quickstart
==========

To get started using Flask-Funnel simply add the following to your Flask app::

    from flask import Flask
    from flask.ext.import Funnel

    app = Flask(__name__)
    Funnel(app)


Test
====

To run tests from a tarball or git clone::

    $ python setup.py test
