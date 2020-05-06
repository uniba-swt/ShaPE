node(wrapper).
alpha(wrapper, n1).
bravo(wrapper, b1).

node(n1).
node(n2).
node(n3).

next(n1, n2).
next(n2, n3).
next(n3, null).

node(b1).
node(b2).
node(b3).
node(b4).
node(b5).

next(b1, b2).
next(b2, b3).
next(b3, b4).
next(b4, b5).
next(b5, null).

entrypoint(wrapper).