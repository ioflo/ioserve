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
from ioflo.aid.timing import StoreTimer
from ioflo.base import Store
from ioflo.aio import WireLog
from ioflo.aio.http import Valet, Patron
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
        Test Valet Patron and Bottle
        """
        console.terse("{0}\n".format(self.testBasic.__doc__))

        store = Store(stamp=0.0)

        app = bottle.default_app() # create bottle app

        @app.get('/echo')
        @app.get('/echo/<action>')
        @app.post('/echo')
        @app.post('/echo/<action>')
        def echoGet(action=None):
            """
            Echo back request data
            """
            query = dict(bottle.request.query.items())
            body = bottle.request.json
            raw = bottle.request.body.read()
            form = odict(bottle.request.forms)

            data = odict(verb=bottle.request.method,
                        url=bottle.request.url,
                        action=action,
                        query=query,
                        form=form,
                        content=body)
            return data


        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = Valet(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store,
                              app=app)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = Patron(bufsize=131072,
                      wlog=wireLogBeta,
                      store=store,
                      path=path,
                      reconnectable=True)

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                        ])

        beta.requests.append(request)
        timer = StoreTimer(store, duration=1.0)
        while (beta.requests or beta.connector.txes or not beta.responses or
               not alpha.idle()):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['reason'], 'OK')
        self.assertEqual(response['body'],bytearray(b''))
        self.assertEqual(response['data'],{'action': None,
                                            'content': None,
                                            'form': {},
                                            'query': {'name': 'fame'},
                                            'url': 'http://localhost:6101/echo?name=fame',
                                            'verb': 'GET'},)

        responder = alpha.reps.values()[0]
        self.assertTrue(responder.status.startswith, str(response['status']))
        self.assertEqual(responder.headers, response['headers'])

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testLoadTestEnds(self):
        """
        Test behavior
        """
        console.terse("{0}\n".format(self.testLoadTestEnds.__doc__))

        store = Store(stamp=0.0)

        app = bottle.default_app() # create bottle app

        ending.loadTest(app, store)

        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = Valet(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store,
                              app=app)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = Patron(bufsize=131072,
                      wlog=wireLogBeta,
                      store=store,
                      path=path,
                      reconnectable=True)

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        # get echo
        request = odict([('method', u'GET'),
                         ('path', u'/test/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                        ])

        beta.requests.append(request)
        timer = StoreTimer(store, duration=1.0)
        while (beta.requests or beta.connector.txes or not beta.responses or
               not alpha.idle()):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['reason'], 'OK')
        self.assertEqual(response['body'],bytearray(b''))
        self.assertEqual(response['data'],{'action': None,
                                            'body': '',
                                            'data': None,
                                            'form': odict([]),
                                            'headers': {'Accept': 'application/json',
                                                        'Accept-Encoding': 'identity',
                                                        'Content-Length': '0',
                                                        'Content-Type': '',
                                                        'Host': 'localhost:6101'},
                                            'query': odict([('name', 'fame')]),
                                            'url': 'http://localhost:6101/test/echo?name=fame',
                                            'verb': 'GET'},)

        responder = alpha.reps.values()[0]
        self.assertTrue(responder.status.startswith, str(response['status']))
        self.assertEqual(responder.headers, response['headers'])

        # get routes
        request = odict([('method', u'GET'),
                         ('path', u'/test/route'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                        ])

        beta.requests.append(request)
        timer = StoreTimer(store, duration=1.0)
        while (beta.requests or beta.connector.txes or not beta.responses or
               not alpha.idle()):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['reason'], 'OK')
        self.assertEqual(response['body'], bytearray(
                b'Web app file is located at /Data/Code/public/ioserve/ios'
                b'erve/end\n/echo/<action> POST\n/echo POST\n/echo/<actio'
                b'n> GET\n/echo GET\n/ GET\n/test GET\n/test/route GET\n/te'
                b'st/echo POST\n/test/echo/<action> POST\n/test/echo GET'
                b'\n/test/echo/<action> GET\n/test/auth POST\n/test/auth/'
                b'<token> POST\n/test/auth GET\n/test/auth/<token> GET\n/'
                b'test/stream GET'))
        self.assertEqual(response['data'],{
                            'action': None,
                            'body': '',
                            'data': None,
                            'form': odict([]),
                            'headers': {'Accept': 'application/json',
                                        'Accept-Encoding': 'identity',
                                        'Content-Length': '0',
                                        'Content-Type': '',
                                        'Host': 'localhost:6101'},
                            'query': odict([('name', 'fame')]),
                            'url': 'http://localhost:6101/test/echo?name=fame',
                            'verb': 'GET'},)

        responder = alpha.reps.values()[0]
        self.assertTrue(responder.status.startswith, str(response['status']))
        self.assertEqual(responder.headers, response['headers'])

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testTestStream(self):
        """
        Test Valet WSGI service request response stream sse
        """
        console.terse("{0}\n".format(self.testTestStream.__doc__))

        store = Store(stamp=0.0)

        app = bottle.default_app() # create bottle app

        ending.loadTest(app, store)

        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = Valet(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store,
                              app=app)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     store=store,
                                     path=path,
                                     reconnectable=True)

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/test/stream'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                         ('body', None),
                        ])

        beta.requests.append(request)
        timer = StoreTimer(store, duration=1.0)
        while (not timer.expired):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})


        #timed out while stream still open so no responses in .responses
        self.assertIs(beta.waited, True)
        self.assertIs(beta.respondent.ended, False)
        self.assertEqual(len(beta.responses), 0)
        self.assertIn('content-type', beta.respondent.headers)
        self.assertEqual(beta.respondent.headers['content-type'], 'text/event-stream')
        self.assertIn('transfer-encoding', beta.respondent.headers)
        self.assertEqual(beta.respondent.headers['transfer-encoding'], 'chunked')

        self.assertTrue(len(beta.events) >= 3)
        self.assertEqual(beta.respondent.retry, 1000)
        self.assertTrue(int(beta.respondent.leid) >= 2)
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': '1'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': '2'})
        beta.events.clear()

        #keep going until ended
        timer.restart(duration=1.5)
        while (not timer.expired):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertTrue(len(beta.events) >= 3)
        self.assertEqual(beta.respondent.leid,  '9')
        self.assertEqual(beta.events[-2], {'id': '9', 'name': '', 'data': '9'})
        self.assertEqual(beta.events[-1], {'id': '9', 'name': '', 'data': 'END'})
        beta.events.clear()

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


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
             'testLoadTestEnds',
             'testTestStream',
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
