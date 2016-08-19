#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 07:47:41 2016

@author: andyjones
"""
from tbtools import get_current_traceback, render_console_html
from werkzeug.debug.console import Console
from flask import Flask, request, Response

app = Flask(__name__, static_folder='resources')

TRACEBACK = None
CONSOLE_FRAME = None

class _ConsoleFrame(object):
    def __init__(self, namespace):
        self.console = Console(namespace)
        self.id = 0

@app.route('/debugger')
def debug():
    return Response(
                    response=TRACEBACK.render_full(evalex=True, evalex_trusted=True),
                    headers={'X-XSS-Protection': '0'} # The debug output can trigger Chrome's XSS protection
                    )

@app.route('/command')
def command():
    frame_id = request.args.get('frm', type=int)
    if frame_id > 0:
        frame = [f for f in TRACEBACK.frames if f.id == frame_id][0]
    else:
        frame = CONSOLE_FRAME

    command = request.args.get('cmd')
    return frame.console.eval(command)
    
@app.route('/console')
def console():
    return render_console_html(evalex_trusted=True)
    
def post_mortem():
    global TRACEBACK, CONSOLE_FRAME
    TRACEBACK = get_current_traceback()
    CONSOLE_FRAME = _ConsoleFrame({})
    app.run()
    
try:
    raise ValueError()
except:
    post_mortem()