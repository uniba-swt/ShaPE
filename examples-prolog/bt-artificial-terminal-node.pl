node(n1).
node(n2).
node(n3).
node(n4).
node(n5).
node(n6).
node(n7).
node(n8).

left(n1, n2).
left(n2, n4).
left(n3, n6).
left(n4, n8).
left(n5, n8).
left(n6, n8).
left(n7, n8).
left(n8, null).

right(n1, n3).
right(n2, n5).
right(n3, n7).
right(n4, n8).
right(n5, n8).
right(n6, n8).
right(n7, n8).
right(n8, null).

entrypoint(n1).
entrypoint(n8).