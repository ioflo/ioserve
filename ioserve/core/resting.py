# -*- coding: utf-8 -*-
"""
Behaviors for Rest API
"""
from __future__ import absolute_import, division, print_function

import sys
import os

# Import Python libs
from collections import deque
try:
    import simplejson as json
except ImportError:
    import json

import bottle

# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid import odict
from ioflo.aid import getConsole
from ioflo.aio import WireLog
from ioflo.aio.http import Valet
from ioflo.base import doify

from ..end import ending
#from ..help import bottle

console = getConsole()

"""
Usage pattern

frame server
  do ioserve server open at enter
  do ioserve server service
  do ioserve server close at exit


"""

@doify('IoserveServerOpen', ioinits=odict(valet="", mock="", test=""))
def ioserveServerOpen(self, buffer=False, **kwa):
    """
    Setup and open a rest server

    Ioinit attributes
        valet is Valet instance (wsgi server)
        mock is Flag if True load mock service endpoints
        test if Flag if True load test endpoints

    Parameters:
        buffer is boolean If True then create wire log buffer for Valet

    Context: enter

    Example:
        do ioserve server open at enter
    """
    if buffer:
        wlog = WireLog(buffify=True,  same=True)
        result = wlog.reopen()
    else:
        wlog = None
    app = bottle.app() # create bottle app
    test = True if self.test.value else False
    mock = True if self.mock.value else False
    ending.loadAll(app, self.store, mock=mock, test=test)
    self.valet.value = Valet(port=8080,
                             bufsize=131072,
                             wlog=wlog,
                             store=self.store,
                             app=app,
                             )

    result = self.valet.value.servant.reopen()
    if not result:
        console.terse("Error opening server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.eha))
        return


    console.concise("Opened server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.eha,))

@doify('IoserveServerService',ioinits=odict(valet=""))
def ioserveServerService(self, **kwa):
    """
    Service server given by valet

    Ioinit attributes:
        valet is a Valet instance

    Context: recur

    Example:
        do ioserve server service
    """
    if self.valet.value:
        self.valet.value.serviceAll()


@doify('IoserveServerClose', ioinits=odict(valet=""))
def ioserveServerClose(self, **kwa):
    """
    Close server in valet

    Ioinit attributes:
        valet is a Valet instance

    Context: exit

    Example:
        do ioserve server close at exit
    """
    if self.valet.value:
        self.valet.value.servant.close()

        console.concise("Closed server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.eha))


