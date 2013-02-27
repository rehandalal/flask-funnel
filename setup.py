import os
from setuptools import setup

ROOT = os.path.abspath(os.path.dirname(__file__))

setup(
    name='Flask-Funnel',
    version='0.1',
    url='http://github.com/rehandalal/flask-funnel/',
    license='BSD',
    author='Rehan Dalal',
    author_email='rehan@meet-rehan.com',
    description='Asset management for Flask.',
    long_description=open(os.path.join(ROOT, 'docs/index.rst')).read(),
    packages=['flask_funnel'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-Script'
    ],
    test_suite='flask_funnel.tests.suite',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
