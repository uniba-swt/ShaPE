node(n1).
node(n2).
node(n3).
node(n4).

next(n1, n2).
next(n2, n3).
next(n3, n4).
next(n4, n1).

prev(n1, null).
prev(n2, n1).
prev(n3, n2).
prev(n4, n3).

entrypoint(n1).