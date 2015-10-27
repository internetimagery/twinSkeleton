# Vector stuff

import math

class Vector(object):
    def __init__(s, x=0.0, y=0.0, z=0.0):
        s.vec = [float(x), float(y), float(z)]
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
    def __add__(s, v): return s.__class__(*[a + b for a, b in zip(s, v)])
    def __div__(s, v): return s.__class__(*[a / b for a, b in zip(s, v)])
    def __truediv__(s, v): return s.__class__(*[a / b for a, b in zip(s, v)])
    def __floordiv__(s, v): return s.__class__(*[a // b for a, b in zip(s, v)])
    def __mod__(s, v): return s.__class__(*[a % b for a, b in zip(s, v)])
    def __mul__(s, v): return s.__class__(*[a * b for a, b in zip(s, v)])
    def __neg__(s): return s.__class__(*[-a for a in s])
    def __pos__(s): return s.__class__(*[+a for a in s])
    def __pow__(s, v): return s.__class__(*[a ** b for a, b in zip(s, v)])
    def __sub__(s, v): return s.__class__(*[a - b for a, b in zip(s, v)])
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
            return math.sqrt(s ** (2.0,2.0,2.0))
        return locals()
    length = property(**length())
    def cross(s, v):
        return s.__class__(*[
            s[1] * v[2] - s[2] * v[1],
            s[2] * v[0] - s[0] * v[2],
            s[0] * v[1] - s[1] * v[0]
            ])
    def angle(s, v): math.degrees(math.acos(s.dot(v) / (s.length * v.length) ))
    def parallel(s, *v):
        v = list(v)
        v.append(s)
        return [[b[a] for b in v] for a in range(3)]
    def min(s, *v):
        v = s.parallel(*v)
        return s.__class__(min(v[0]), min(v[1]), min(v[2]))
    def max(s, *v):
        v = s.parallel(*v)
        return s.__class__(max(v[0]), max(v[1]), max(v[2]))
    def distance(s, v): return math.sqrt( sum((s - v) ** (2.0,2.0,2.0) ))

# poly = [
#     Vector(10,10,0), Vector(-10,10,0), Vector(10,-10,0), Vector(-10,-10,0), Vector(10,10,10), Vector(-10,10,10), Vector(10,-10,10), Vector(-10,-10,10)
#     ]
# pointIn = Vector(0,0,5)
# pointOut = Vector(-200,0,0)
#
# def AngleSum(point, poly):
#     anglesum = 0
#     polyNum = len(poly)
#     for i in range(polyNum):
#         p1 = poly[i] - point
#         p2 = poly[(i + 1) % polyNum] - point
#
#         mag = p1.magnitude * p2.magnitude
#         if mag <= 0.000001:
#             return math.pi * 2 # Actually on a point
#         else:
#             costheta = (sum(p1 * p2) / mag) if mag else 0
#         anglesum += math.acos(costheta)
#     return anglesum
#
# print math.degrees(AngleSum(pointIn, poly))
# print math.degrees(AngleSum(pointOut, poly))
