# -*- coding: utf-8 -*-
"""
API Endpoints
"""
from __future__ import absolute_import, division, print_function

import sys
import os
import time

# Import Python libs
from collections import deque
try:
    import simplejson as json
except ImportError:
    import json
import uuid


# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid.odicting import odict
from ioflo.aid.timing import StoreTimer, tuuid
from ioflo.aid.byting import hexify, unhexify
from ioflo.aid import getConsole


from  ..help import bottle

console = getConsole()

def loadAll(app, store, test=False):
    """
        Load endpoints into wsgi app with store reference
        This function essentially wraps the endpoint definitions with a scope
        that includes a reference to the data store
    """
    if test:
        loadTest(app, store)

    loadEnds(app, store)
    loadCors(app)
    loadErrors(app)


def loadEnds(app, store):
    """
    Load endpoints for api with store reference
    This function essentially wraps the endpoint definitions with a scope
    that includes a reference to the data store
    """

    return app


def loadTest(app, store):
    """
    Load test endpoints into wsgi app with store reference
    This function essentially wraps the endpoint definitions with a scope
    that includes a reference to the data store
    """

    @app.get(['/', '/test', '/test/route'])
    def testGet():
        """
        Test endpoint for bottle application routes
        Shows location of this file
        Shows all routes in current bottle app
        """
        bottle.response.set_header('content-type', 'text/plain')
        content = "Web app file is located at %s" % os.path.dirname(os.path.abspath(__file__))
        siteMap = ""

        for route in app.routes:
            siteMap = "%s%s%s %s" % (siteMap, '\n' if siteMap else '', route.rule, route.method)
            target = route.config.get('mountpoint', {}).get('target')
            if target:
                for way in target.routes:
                    siteMap = "%s\n    %s %s" % (siteMap, way.rule, way.method)

        content = "%s\n%s" % (content, siteMap)
        return content

    @app.get(['/test/echo', '/test/echo/<action>'])
    @app.post(['/test/echo', '/test/echo/<action>'])
    def echoTest(action=None):
        """
        Ajax test endpoint for web application service
        Echos back args as content
        """
        # convert to json serializible dict
        result = odict(verb=bottle.request.method,
                       url=bottle.request.url,
                       action=action,
                       query=odict(bottle.request.query.items()),
                       headers=odict(bottle.request.headers.items()),
                       data=bottle.request.json,
                       form=odict(bottle.request.forms),
                       body=bottle.request.body.read())

        return result

    @app.get(['/test/auth', '/test/auth/<token>'])
    @app.post(['/test/auth', '/test/auth/<token>'])
    def authTest(token=None):
        """
        Auth credentials in body data as json
        or query parameters
        or token from end of url path
        or token from X-Auth-Token header
        """
        if not token:
            token = bottle.request.get_header('X-Auth-Token')

        data = bottle.request.json
        if not token:
            user = data.get('user')
            password = data.get('password')

        query = odict(bottle.request.query.items())
        if not user or not password:
            user = query.get('user')
            password = query.get('password')

        if not token and (not user or not password):
            bottle.abort(400, "Authentication credentials missing.")

        result = odict(token=token,
                       user=user,
                       password=password,
                       headers=odict(bottle.request.headers.items()),
                       query=query,
                       data=data,
                      )
        return result

    @app.get('/test/stream')
    def streamTest():
        """
        Create test server sent event stream that sends count events
        """
        timer = StoreTimer(store, duration=2.0)
        bottle.response.set_header('Content-Type',  'text/event-stream') #text
        bottle.response.set_header('Cache-Control',  'no-cache')
        # Set client-side auto-reconnect timeout, ms.
        yield 'retry: 1000\n\n'
        i = 0
        yield 'id: {0}\n'.format(i)
        i += 1
        yield 'data: START\n\n'
        n = 1
        while not timer.expired:
            yield 'id: {0}\n'.format(i)
            i += 1
            yield 'data: {0}\n\n'.format(n)
            n += 1
        yield "data: END\n\n"

    return app

def loadCors(app):
    """
    Load support for CORS Cross Origin Resource Sharing
    """
    corsRoutes = ['/',
                  '/test', '/test/routes', '/test/echo', '/test/echo/<action>',
                  '/test/auth', '/test/auth/<token>',
                  'test/stream',
                  ]

    @app.hook('after_request')
    def enableCors():
        """
        Add CORS headers to each response
        Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
        """
        # bottle.response.set_header('Access-Control-Allow-Credentials', 'true')
        bottle.response.set_header('Access-Control-Max-Age:', '3600')
        bottle.response.set_header('Access-Control-Allow-Origin', '*')
        bottle.response.set_header('Access-Control-Allow-Methods',
                                   'PUT, GET, POST, DELETE, OPTIONS')
        bottle.response.set_header('Access-Control-Allow-Headers',
                                   'Origin, Accept, Content-Type, X-Requested-With,'
                                   ' X-CSRF-Token, X-Auth-Token')

    @app.route(corsRoutes, method='OPTIONS')
    def allowOption(path=None, **kwa):
        """
        Respond to OPTION request method
        """
        return {}

    return app


def loadErrors(app):
    """
    Load decorated Error functions for bottle web application
    Error functions do not automatically jsonify dicts so must manually do so.
    """

    @app.error(400)
    def error400(ex):
        """
        Bad Request
        """
        bottle.response.set_header('content-type', 'application/json')
        return json.dumps(dict(error=ex.body))

    @app.error(401)
    def error401(ex):
        """
        Unauthorized
        """
        bottle.response.set_header('content-type', 'application/json')
        return json.dumps(dict(error=ex.body))

    @app.error(404)
    def error404(ex):
        """
        Not Found
        """
        bottle.response.set_header('content-type', 'application/json')
        return json.dumps(dict(error=ex.body))

    @app.error(405)
    def error405(ex):
        """
        Method Not Allowed
        """
        bottle.response.set_header('content-type', 'application/json')
        return json.dumps(dict(error=ex.body))

    @app.error(409)
    def error409(ex):
        """
        Conflict
        """
        bottle.response.set_header('content-type', 'application/json')
        return json.dumps(dict(error=ex.body))

    @app.error(503)
    def error503(ex):
        """
        Service Unavailable
        """
        bottle.response.set_header('content-type', 'application/json')
        return json.dumps(dict(error=ex.body))


def abortify(app, code=500, text="Unknown Error"):
    """
    Fixup error when in async coro endpoint
    """
    ex = bottle.HTTPError(code, text)
    ex.apply(bottle.response)
    ex.body = app.error_handler.get(ex.status_code,
                                app.default_error_handler)(ex)
    #ex.body = b"".join(app._cast(ex.body))
    raise ex


def rebase(base):
    """ Create new app using current app routes prefixed with base"""
    if not base:  # no rebase needed
        return bottle.app()

    oldApp = bottle.app.pop()
    newApp = bottle.app.push()
    for route in oldApp.routes:
        route.rule = "{0}{1}".format(base, route.rule)
        newApp.add_route(route)
        route.reset()  # reapply plugins on next call
    return newApp
