import os
import re
from setuptools import setup


ROOT = os.path.abspath(os.path.dirname(__file__))
VERSIONFILE = os.path.join('flask_mobility', '_version.py')
VSRE = r"""^__version__ = ['"]([^'"]*)['"]"""


def get_version():
    verstrline = open(VERSIONFILE, 'rt').read()
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError(
            'Unable to find version string in {0}.'.format(VERSIONFILE))


setup(
    name='Flask-Funnel',
    version=get_version(),
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
