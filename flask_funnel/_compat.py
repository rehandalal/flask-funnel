from __future__ import absolute_import

import sys


__all__ = ["IS_PY2", "IS_PY3", "urlopen", "URLError", "HTTPError"]


IS_PY2 = (sys.version_info[0] == 2)
IS_PY3 = (sys.version_info[0] == 3)


if IS_PY2:
    from urllib2 import urlopen, URLError, HTTPError

if IS_PY3:
    from urllib.request import urlopen, URLError, HTTPError  # noqa
