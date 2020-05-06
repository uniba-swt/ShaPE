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

node(b1n1).
next(b1n1, null).

node(b2n1).
next(b2n1, b2n2).
node(b2n2).
next(b2n2, null).

node(b3n1).
next(b3n1, b3n2).
node(b3n2).
next(b3n2, null).

node(b5n1).
next(b5n1, null).

node(b4n1).
next(b4n1, null).

child(b1, b1n1).
child(b2, b2n1).
child(b3, b3n1).
child(b4, b4n1).
child(b5, b5n1).

entrypoint(b1).