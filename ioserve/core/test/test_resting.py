# -*- coding: utf-8 -*-
"""
Unittests for rest endpoint behaviors
"""

import sys
import os
import time

import unittest

try:
    import simplejson as json
except ImportError:
    import json


# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid import odict
from ioflo.aid import getConsole
from ioflo.base import Store
from ioflo.test import testing

console = getConsole()

from ioserve.help import bottle
from ioserve.end import ending

def setUpModule():
    pass

def tearDownModule():
    pass


class BasicTestCase(unittest.TestCase):
    """
    Test Case
    """

    def setUp(self):
        """

        """
        console.reinit(verbosity=console.Wordage.profuse)

    def tearDown(self):
        """

        """
        console.reinit(verbosity=console.Wordage.concise)


    def testBasic(self):
        """
        Test behavior
        """
        console.terse("{0}\n".format(self.testBasic.__doc__))



def runOne(test):
    '''
    Unittest Runner
    '''
    test = BasicTestCase(test)
    suite = unittest.TestSuite([test])
    unittest.TextTestRunner(verbosity=2).run(suite)

def runSome():
    """ Unittest runner """
    tests =  []
    names = [
             'testBasic',
            ]
    tests.extend(map(BasicTestCase, names))
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

def runAll():
    """ Unittest runner """
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BasicTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__' and __package__ is None:

    #

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testBasic')
