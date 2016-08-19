#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 07:47:41 2016

@author: andyjones
"""
import mimetypes
from os.path import join, dirname, basename, isfile, abspath
from werkzeug.wrappers import BaseRequest as Request, BaseResponse as Response
from werkzeug.debug.tbtools import get_current_traceback, render_console_html
from werkzeug.debug.console import Console
from werkzeug.serving import run_simple

class _ConsoleFrame(object):

    """Helper class so that we can reuse the frame console code for the
    standalone console.
    """

    def __init__(self, namespace):
        self.console = Console(namespace)
        self.id = 0

class DebuggedApplication(object):

    def __init__(self):
        self.traceback = get_current_traceback()
        self.frames = {f.id: f for f in self.traceback.frames}

    def debug_application(self, environ, start_response):
        """Run the application and conserve the traceback frames."""

        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=utf-8'),
            # Disable Chrome's XSS protection, the debug
            # output can cause false-positives.
            ('X-XSS-Protection', '0'),
        ])
        yield self.traceback.render_full(evalex=True, evalex_trusted=True).encode('utf-8', 'replace')

    def execute_command(self, request, command, frame):
        """Execute a command in a console."""
        return Response(frame.console.eval(command), mimetype='text/html')

    def display_console(self, request):
        """Display a standalone shell."""
        if 0 not in self.frames:
            #TODO: Point this at some useful namespace? 
            ns = {}
            self.frames[0] = _ConsoleFrame(ns)
            
        return Response(render_console_html(evalex_trusted=True, secret=0), mimetype='text/html')

    def get_resource(self, request, filename):
        """Return a static resource from the shared folder."""
        filename = join(dirname(abspath(__file__)), 'resources', basename(filename))
        if isfile(filename):
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            f = open(filename, 'rb')
            try:
                return Response(f.read(), mimetype=mimetype)
            finally:
                f.close()
        return Response('Not Found', status=404)

    def __call__(self, environ, start_response):
        """Dispatch the requests."""
        # important: don't ever access a function here that reads the incoming
        # form data!  Otherwise the application won't have access to that data
        # any more!
        request = Request(environ)
        response = self.debug_application
        if request.args.get('__debugger__') == 'yes':
            cmd = request.args.get('cmd')
            arg = request.args.get('f')
            frame = self.frames.get(request.args.get('frm', type=int))
            if cmd == 'resource' and arg:
                response = self.get_resource(request, arg)
            elif cmd is not None and frame is not None:
                response = self.execute_command(request, cmd, frame)
        elif request.path == '/console':
            response = self.display_console(request)
        return response(environ, start_response)
    
def post_mortem():
    run_simple('localhost', 4001, DebuggedApplication())
    
try:
    raise ValueError()
except:
    post_mortem()