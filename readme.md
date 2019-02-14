**NEVER RUN THIS ON A PUBLIC PORT. ANYONE WHO HAS ACCESS TO IT CAN RUN ARBITRARY CODE ON THE HOST COMPUTER**

This is a remote debugger for Python with a web interface. It is based on the fantastic [Werkzeug debugger](https://github.com/pallets/werkzeug).

To use it, call `webpdb.pm(host, port)` from inside an `except` block. It'll launch a web server at the given host and port, which you can access at `host:port`. You should get a webpage like this:

![Example debug screen](readme_example.png)

which displays the most recent error, and lets you create a console anywhere on that error's stack.

### External Access

As mentioned at the top of the readme, _never run this on a public port_. By default, the host is `localhost`, which means it's only accessible from the computer running the debugger. If you're working in a private cluster and want to access it from another computer, set the host to `0.0.0.0`. 

### Example

```python
def f():
  raise ValueError()

try:
    f()
except:
    webpdb.pm()
```

Now open your browser and navigate to [localhost:5001](http://localhost:5001). Click on any of the stack frames to open a primitive console.

### Installation

```pip install webpdb```

### TODO
  * *Add password/token authentication like Werkzeug has.*
  * Replace the underlying REPL with something that calls out to ipython
  * Add syntax highlighting of some sort
  * Add a 'kill this process' button.
