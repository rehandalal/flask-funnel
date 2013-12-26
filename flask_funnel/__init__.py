from __future__ import absolute_import

from ._version import __releasedate__, __version__  # noqa
from .manager import manager
from .main import Funnel


__all__ = ['Funnel', 'manager']
