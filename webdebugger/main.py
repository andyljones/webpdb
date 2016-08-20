#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 07:47:41 2016

@author: andyjones
"""
import sys
from flask import Flask, request, Response

from .tbtools import Traceback

app = Flask(__name__, static_folder='resources')
traceback = None


@app.route('/debugger')
def debug():
    return Response(
                    response=traceback.render(),
                    headers={'X-XSS-Protection': '0'} # The debug output can trigger Chrome's XSS protection
                    )

    
@app.route('/command')
def command():
    frame_id = request.args.get('frm', type=int)
    frame = [f for f in traceback.frames if f.id == frame_id][0]

    command = request.args.get('cmd')
    return frame.console.eval(command)
    
    
def post_mortem():
    global traceback
    traceback = Traceback(*sys.exc_info())
    app.run()
    
    
if __name__ == '__main__':
    def f():
        if True:
            raise ValueError('Problem!')
    
    try:
        f()
    except:
        post_mortem()