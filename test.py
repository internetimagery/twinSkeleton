
#testing
import collections

vec = collections.namedtuple("vec", "x y z")

p1 = vec(1,2,3)
p2 = vec(2,3,4)

class Vector(collections.Sequence):
    def __init__(s, *args):
        s._len = len(args)
        s._vec = args
        s.__dict__["__add__"] = lambda x, y: y
    def __getitem__(s, k): return s._vec[k]
    def __repr__(s): return "Vector %s" % repr(s._vec)
    def __len__(s): return s._len
    def __getattribute__(s, k):
        print "get", k
        return collections.Sequence.__getattribute__(s, k)
    pass

class P(type):
    def __init__(s): pass
    def __getattr__(s, k):
        print "Get", k
        return getattr(type, k)

p = P()
print p
