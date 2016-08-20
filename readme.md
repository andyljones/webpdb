THERE IS NO SECURITY ON THIS. DO NOT RUN IT ON A PUBLIC PORT. ANYONE WHO HAS ACCESS TO IT CAN RUN ARBITRARY CODE ON THE HOST COMPUTER.

This is a remote debugger for Python with a web interface. It is based on the fantastic [Werkzeug debugger](https://github.com/pallets/werkzeug).

To use it, call `webdebugger.post_mortem(host, port)` from inside an `except` block. It'll launch a web server at the given host and port, and provide you with a console that you can use to inspect the error.

See [example.py](example.py) for an example.

Currently Python 3 only.
