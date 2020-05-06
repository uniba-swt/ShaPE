node(n1).
node(n2).
node(n3).

next(n1, n2).
next(n2, n3).
next(n3, null).

prev(n1, null).
prev(n2, n1).
prev(n3, null).

entrypoint(n1).