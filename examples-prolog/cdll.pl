node(n1).
node(n2).
node(n3).
node(n4).
node(n5).

next(n1, n2).
next(n2, n3).
next(n3, n4).
next(n4, n5).
next(n5, n1).

prev(n1, n5).
prev(n2, n1).
prev(n3, n2).
prev(n4, n3).
prev(n5, n4).

entrypoint(n1).