node(n1t2).
node(n2t2).
node(n3t2).
node(n4t2).

left(n1t2, n2t2).
left(n2t2, n4t2).
left(n3t2, null).
left(n4t2, null).

right(n1t2, n3t2).
right(n2t2, null).
right(n3t2, null).
right(n4t2, null).

entrypoint(n1t2).