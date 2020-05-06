node(head).
node(inner1).
node(inner2).
node(inner3).
node(inner4).
node(tail).

next(head, inner1).
next(inner1, inner2).
next(inner2, inner3).
next(inner3, inner4).
next(inner4, tail).
next(tail, null).

entrypoint(head).
entrypoint(tail).