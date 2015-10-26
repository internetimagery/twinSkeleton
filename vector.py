# Vector stuff

import math

class Vector(object):
    def __init__(s, x=0.0, y=0.0, z=0.0):
        s.vec = [x, y, z]
    def __getitem__(s, k): return s.vec[k]
    def __setitem__(s, k, v): s.vec[k] = v
    def __iter__(s): return iter(s.vec)
    def __len__(s): return len(s.vec)
    def __repr__(s): return "Vector: %s" % repr(s.vec)
    def __nonzero__(s): return True if s[0] and s[1] and s[2] else False
    def __eq__(s, v): return True if s[0] == v[0] and s[1] == v[1] and s[2] == v[2] else False
    def __ne__(s, v): return False if s == v else True
    def __lt__(s, v): return True if s[0] < v[0] and s[1] < v[1] and s[2] < v[2] else False
    def __le__(s, v): return True if s[0] <= v[0] and s[1] <= v[1] and s[2] <= v[2] else False
    def __gt__(s, v): return True if s[0] > v[0] and s[1] > v[1] and s[2] > v[2] else False
    def __ge__(s, v): return True if s[0] >= v[0] and s[1] >= v[1] and s[2] >= v[2] else False
    def __add__(s, v): return s.__class__(*map(lambda x, y: x + y, s, v))
    def __div__(s, v): return s.__class__(*map(lambda x, y: x / y, s, v))
    def __truediv__(s, v): return s.__class__(*map(lambda x, y: x / y, s, v))
    def __floordiv__(s, v): return s.__class__(*map(lambda x, y: x // y, s, v))
    def __mod__(s, v): return s.__class__(*map(lambda x, y: x % y, s, v))
    def __mul__(s, v): return s.__class__(*map(lambda x, y: x * y, s, v))
    def __neg__(s): return s.__class__(*map(lambda x: -x, s))
    def __pos__(s): return s.__class__(*map(lambda x: +x, s))
    def __pow__(s, v): return s.__class__(*map(lambda x, y: x ** y, s, v))
    def __sub__(s, v): return s.__class__(*map(lambda x, y: x - y, s, v))
    def dot(s, v): return sum(s * v)
    def magnitude():
        def fget(s):
            return math.sqrt(sum(s * s))
        return locals()
    magnitude = property(**magnitude())
    def normalized():
        def fget(s):
            m = s.magnitude
            return s / (m,m,m) if m else s.__class__(0,0,0)
        return locals()
    normalized = property(**normalized())
    def length():
        def fget(s):
            return math.sqrt(s ** (2,2,2))
        return locals()
    length = property(**length())
    def cross(s, v):
        return s.__class__(*[
            s[1] * v[2] - s[2] * v[1],
            s[2] * v[0] - s[0] * v[2],
            s[0] * v[1] - s[1] * v[0]
            ])
    def angle(s, v): math.degrees(math.acos(s.dot(v) / (s.length() * v.length()) ))
