# -*- coding: utf-8 -*-
"""
    werkzeug.debug.tbtools
    ~~~~~~~~~~~~~~~~~~~~~~
    This module provides various traceback related utility functions.
    :copyright: (c) 2014 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD.
"""
import re

import os
import inspect
import traceback
import codecs

from werkzeug.utils import cached_property
from werkzeug._compat import PY2, text_type, to_native, to_unicode
from werkzeug.filesystem import get_filesystem_encoding
from jinja2 import Template

from console import Console

_coding_re = re.compile(br'coding[:=]\s*([-\w.]+)')
_line_re = re.compile(br'^(.*?)$(?m)')
_funcdef_re = re.compile(r'^(\s*def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
UTF8_COOKIE = b'\xef\xbb\xbf'

class Traceback(object):
    """Wraps a traceback."""

    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        if not isinstance(exc_type, str):
            exception_type = exc_type.__name__
            if exc_type.__module__ not in ('__builtin__', 'exceptions'):
                exception_type = exc_type.__module__ + '.' + exception_type
        else:
            exception_type = exc_type
        self.exception_type = exception_type
        
        buf = traceback.format_exception_only(self.exc_type, self.exc_value)
        rv = ''.join(buf).strip()
        self.exception = rv.decode('utf-8', 'replace') if PY2 else rv
        
        self.frames = []
        while tb:
            self.frames.append(Frame(exc_type, exc_value, tb))
            tb = tb.tb_next
            
        self.id = id(self)

    def render(self):
        """Render the Full HTML page with the traceback info."""            
        frames = [{'id': frame.id,
                   'filename': frame.filename,
                   'lineno': frame.lineno,
                   'function_name': frame.function_name,
                   'lines': frame.line_context(),
                   'current_line': frame.current_line.strip(),
                   } for frame in self.frames]
        
        template = Template(open('templates/debugger.j2').read())
        return template.render(**{
            'console':          'false',
            'title':            self.exception,
            'exception':        self.exception,
            'exception_type':   self.exception_type,
            'traceback_id':     self.id,
            'frames':           frames
        })
        

class Frame(object):

    """A single frame in a traceback."""

    def __init__(self, exc_type, exc_value, tb):
        self.lineno = tb.tb_lineno
        self.function_name = tb.tb_frame.f_code.co_name
        self.locals = tb.tb_frame.f_locals
        self.globals = tb.tb_frame.f_globals

        fn = inspect.getsourcefile(tb) or inspect.getfile(tb)
        if fn[-4:] in ('.pyo', '.pyc'):
            fn = fn[:-1]
        # if it's a file on the file system resolve the real filename.
        if os.path.isfile(fn):
            fn = os.path.realpath(fn)
        self.filename = to_unicode(fn, get_filesystem_encoding())
        self.module = self.globals.get('__name__')
        self.loader = self.globals.get('__loader__')
        self.code = tb.tb_frame.f_code
        self.id = id(self)

        
    def line_context(self, context=5):
        before = self.sourcelines[self.lineno - context - 1:self.lineno - 1]
        after = self.sourcelines[self.lineno:self.lineno + context]
        
        def render_line(line, pos):
            line = line.expandtabs().rstrip() + ' ' # extra space stops empty lines from collapsing
            stripped_line = line.strip()
            prefix = len(line) - len(stripped_line)
            return {'position': pos, 'prefix': ' '*prefix, 'text': stripped_line}

        return [render_line(l, 'before') for l in before] + \
               [render_line(self.current_line, 'current')] + \
               [render_line(l, 'after') for l in after]
   
    @property
    def current_line(self):
        try:
            return self.sourcelines[self.lineno - 1]
        except IndexError:
            return u''

    @cached_property
    def console(self):
        return Console(self.globals, self.locals)

    @cached_property
    def sourcelines(self):
        """The sourcecode of the file as list of unicode strings."""
        # get sourcecode from loader or file
        source = None
        if self.loader is not None:
            try:
                if hasattr(self.loader, 'get_source'):
                    source = self.loader.get_source(self.module)
                elif hasattr(self.loader, 'get_source_by_code'):
                    source = self.loader.get_source_by_code(self.code)
            except Exception:
                # we munch the exception so that we don't cause troubles
                # if the loader is broken.
                pass

        if source is None:
            try:
                f = open(to_native(self.filename, get_filesystem_encoding()),
                         mode='rb')
            except IOError:
                return []
            try:
                source = f.read()
            finally:
                f.close()

        # already unicode?  return right away
        if isinstance(source, text_type):
            return source.splitlines()

        # yes. it should be ascii, but we don't want to reject too many
        # characters in the debugger if something breaks
        charset = 'utf-8'
        if source.startswith(UTF8_COOKIE):
            source = source[3:]
        else:
            for idx, match in enumerate(_line_re.finditer(source)):
                match = _coding_re.search(match.group())
                if match is not None:
                    charset = match.group(1)
                    break
                if idx > 1:
                    break

        # on broken cookies we fall back to utf-8 too
        charset = to_native(charset)
        try:
            codecs.lookup(charset)
        except LookupError:
            charset = 'utf-8'

        return source.decode(charset, 'replace').splitlines()