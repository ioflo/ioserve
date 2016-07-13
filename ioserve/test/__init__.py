# -*- coding: utf-8 -*-
"""
test package

to run all the unit tests

>>> from ioserve import test
>>> test.run()

"""
from __future__ import absolute_import, division, print_function

import sys
import os
import unittest

from ioflo.aid.sixing import *
from ioflo.test import run
from ioflo.aid import getConsole

console = getConsole()
console.reinit(verbosity=console.Wordage.concise)

start = os.path.dirname(os.path.dirname
                        (os.path.abspath
                         (sys.modules.get(__name__).__file__)))

# need top to be above root for relative imports to not go above top level
top = os.path.dirname(start)

if __name__ == "__main__":
    run(top, start)


