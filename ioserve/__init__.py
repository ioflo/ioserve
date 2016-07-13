"""
ioserve package

"""
from __future__ import absolute_import, division, print_function

import sys
import importlib

_modules = ['core']

for m in _modules:
    importlib.import_module(".{0}".format(m), package='ioserve')

from .__metadata__ import *

