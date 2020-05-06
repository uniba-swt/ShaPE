node(wrapper).
alpha(wrapper, n1).
bravo(wrapper, b1).

node(n1).
node(n2).
node(n3).
node(n4).

next(n1, n2).
next(n2, n3).
next(n3, n4).
next(n4, null).

node(b1).
node(b2).
node(b3).
node(b4).
node(b5).

left(b1, b2).
left(b2, b4).
left(b3, null).
left(b4, null).
left(b5, null).

right(b1, b3).
right(b2, null).
right(b3, b5).
right(b4, null).
right(b5, null).

entrypoint(wrapper).