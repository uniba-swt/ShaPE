node(n1).
node(n2).
node(n3).
node(n4).
node(n5).
node(n6).
node(n7).

next(n1, n2).
next(n2, n3).
next(n3, n4).
next(n4, n5).
next(n5, n6).
next(n6, n7).
next(n7, null).

tail(n1, n7).
tail(n2, n7).
tail(n3, n7).
tail(n4, n7).
tail(n5, n7).
tail(n6, n7).
tail(n7, n7).

entrypoint(n1).