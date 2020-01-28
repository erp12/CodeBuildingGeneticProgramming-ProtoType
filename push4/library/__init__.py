import push4.library.op as op
import push4.library.cast as cast
import push4.library.str as s
import push4.library.io as io
import push4.library.collections as coll
from push4.library import control

functions = op.fns + cast.fns + s.fns + io.fns + coll.fns + control.fns

classes = [
    (s.String, s.String_reifiers),
    # (coll.List_, coll.List_reifiers)
]
