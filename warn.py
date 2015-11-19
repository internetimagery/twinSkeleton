# Visual popup on errors. Not an error handler!
# Created By Jason Dixon. http://internetimagery.com
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

import sys

class Warn(object):
    def _err(s, title, message):
        import maya.cmds as cmds
        cmds.confirmDialog(
            t="Uh oh... %s" % title,
            m=message
        )
    def __call__(s, *args, **kwargs):
        with s:
            if len(args) and callable(args[0]):
                return args[0](*args[1:], **kwargs)
            else:
                raise RuntimeError, "Function not provided as first argument."
    def __enter__(s):
        pass
    def __exit__(s, eType, eName, eTrace):
        if eType:
            s._err(eType.__name__, str(eName))
sys.modules[__name__] = Warn()
