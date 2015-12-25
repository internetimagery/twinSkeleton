# Simple Error report mechanism squeezing into mailto: character limit
# Created By Jason Dixon. http://internetimagery.com
#
# Wrap the outermost function calls in the Report class
# As a decorator or as a context manager on the outermost function calls
# For instance, decorate your Main() function,
# or any function that is called directly by a GUI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

### Change these variables to suit ###

CONTACT = "jason.dixon.email@gmail.com" # Who will be emailed?
SUBJECT = "Error Report for Twin Skeleton" # Subject of the email
CONFIRM_MSG = """
OH NO!
There was a problem and a brief error report has been created.
Would you like to send it?
""" # Message in confirm dialog
OVERSIZE_MSG = "Report Continues..." # Message if report is too long and cut off


### Don't change things beyond this point ###

import re
import urllib
import inspect
import datetime
import platform
import functools
import webbrowser

class Report(object):
    """ Report Errors """
    depth = 0 # Follow report depth
    def __init__(s, char_limit=2083):
        s.char_limit = char_limit # Max characters for mailto: (0 = no limit)

    def __call__(s, func):
        """ Decorate a function. Capture and report any errors """
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with s:
                return func(*args, **kwargs)
        return inner

    def __enter__(s): Report.depth += 1

    def __exit__(s, eType, eVal, eTrace):
        """ Report Errors if they happened """
        Report.depth -= 1
        if eType and not Report.depth: # We have an error?
            if s.consent(eType, eVal):
                text = [
                    str(datetime.datetime.now()),
                    platform.platform(),
                    "%s: %s" % (eType.__name__, eVal),
                    s.software()
                    ]
                text += list(s.compact_trace(eTrace))

                url = "mailto:%s?subject=%s&body=%s" % (
                    CONTACT,
                    urllib.quote(SUBJECT),
                    urllib.quote("\n".join(text))
                    )
                if s.char_limit and s.char_limit < len(url): # We've gone too big. Note that at the bottom
                    note = urllib.quote("\n\n%s" % OVERSIZE_MSG)
                    url = url[:s.char_limit - len(note)] + note

                webbrowser.open(url) # Open email!

    def consent(s, eType, eVal):
        """ Ask user to consent to send message """
        try:
            import maya.cmds as cmds # Is Maya active? Ask using their GUI
            answer = cmds.confirmDialog(t=eType.__name__, m=CONFIRM_MSG, b=("Yes","No"), db="Yes", cb="No", ds="No")
            return "Yes" == answer
        except ImportError:
            return True # No means to ask? Ah well ...

    def software(s):
        """ Return information about software """
        try:
            import maya.mel as mel
            version = mel.eval("$tmp = getApplicationVersionAsFloat();")
            return "Maya, %s" % version
        except ImportError:
            pass
        return "Unknown software."

    def compact_trace(s, trace):
        """ Format traceback compactly """
        filepath = None
        for frame, path, line, func, context, i in reversed(inspect.trace()):
            code = context[i].strip()

            # Tell us which file and function we are in!
            if filepath == path: # Skip repeating filename
                yield "In \"%s\":" % func
            else:
                filepath = path
                yield "In \"%s\" %s:" % (func, path)

            # Tell us the line number and code
            yield "<%s> %s" % (line, code)

            # Tell us the value of relevant variables (attributes using dot notation)
            all_vars = dict(frame.f_globals, **frame.f_locals)
            tokens = set(re.split(r"[^\w\.]+", code))
            tokens |= set(b for a in tokens for b in a.split(".")) # Add in partial names
            for a, b in all_vars.iteritems():
                for var, val in s.collect_vars(tokens, a, b):
                    if var != func:
                        yield "%s=%s" % (var, repr(val))

    def collect_vars(s, code, var, val):
        """ Collect relevant variables """
        if var in code:
            yield var, val
            for attr in dir(val):
                for a in s.collect_vars(code, ".".join((var, attr)), getattr(val, attr)):
                    yield a
