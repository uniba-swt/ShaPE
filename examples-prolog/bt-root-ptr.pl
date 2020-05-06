node(n1).
node(n2).
node(n3).
node(n4).
node(n5).

left(n1, n2).
left(n2, n4).
left(n3, null).
left(n4, null).
left(n5, null).

right(n1, n3).
right(n2, null).
right(n3, n5).
right(n4, null).
right(n5, null).

root(n1, n1).
root(n2, n1).
root(n3, n1).
root(n4, n1).
root(n5, n1).

entrypoint(n1).