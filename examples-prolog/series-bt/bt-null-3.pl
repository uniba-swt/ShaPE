node(n1t3).
node(n2t3).
node(n3t3).
node(n4t3).
node(n5t3).

left(n1t3, n2t3).
left(n2t3, n4t3).
left(n3t3, null).
left(n4t3, null).
left(n5t3, null).

right(n1t3, n3t3).
right(n2t3, null).
right(n3t3, n5t3).
right(n4t3, null).
right(n5t3, null).

entrypoint(n1t3).