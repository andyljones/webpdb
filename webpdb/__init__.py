import sys
from flask import Flask, request, Response

from .tbtools import Traceback

__all__ = ('pm',)

app = Flask(__name__, static_folder='resources')
traceback = None

@app.route('/')
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
    
    
def pm(host='localhost', port=5001):
    """Launches a post-mortem debugger for the most recent exception at the given host and port
    
    Args:
        host (str): the host to launch the debugger on.
        port (int): the port to launch the debugger on.
    """
    global traceback
    traceback = Traceback(*sys.exc_info())
    app.run(host, port)
