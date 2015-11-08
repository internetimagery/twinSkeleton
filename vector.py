# Vector
import math
class Vector(tuple):
    __slots__ = ()
    def __new__(s, *args):
        try: return tuple.__new__(s, args[0])
        except (TypeError, IndexError): return tuple.__new__(s, args)
    def __add__(s, v): return s.__class__(a + b for a, b in zip(s, v))
    def __div__(s, v): return s.__class__(a / b for a, b in zip(s, v))
    def __mod__(s, v): return s.__class__(a % b for a, b in zip(s, v))
    def __mul__(s, v): return s.__class__(a * b for a, b in zip(s, v))
    def __sub__(s, v): return s.__class__(a - b for a, b in zip(s, v))
    def __pow__(s, v): return s.__class__(a ** b for a, b in zip(s, v))
    def __lt__(s, v): return False not in set(a < b for a, b in zip(s, v))
    def __gt__(s, v): return False not in set(a > b for a, b in zip(s, v))
    def __truediv__(s, v): return s.__class__(a / b for a, b in zip(s, v))
    def __eq__(s, v): return False not in set(a == b for a, b in zip(s, v))
    def __le__(s, v): return False not in set(a <= b for a, b in zip(s, v))
    def __ge__(s, v): return False not in set(a >= b for a, b in zip(s, v))
    def __floordiv__(s, v): return s.__class__(a // b for a, b in zip(s, v))
    def angle(s, v): return math.degrees(math.acos(s.dot(v) / (s.magnitude * v.magnitude)))
    normalized = property(lambda s: s / ([s.magnitude]*len(s)) if s else s.__class__([0]*len(s)))
    def __nonzero__(s): return 1 != len(set(a for a in s if not a))
    magnitude = property(lambda s: math.sqrt(sum(s * s))) # |s|
    def __ne__(s, v): return False if s == v else True
    def __neg__(s): return s.__class__(-a for a in s)
    def __pos__(s): return s.__class__(+a for a in s)
    def cross(s, v): return s.__class__(
            s[1] * v[2] - s[2] * v[1],
            s[2] * v[0] - s[0] * v[2],
            s[0] * v[1] - s[1] * v[0])
    def dot(s, v): return sum(s * v)



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
