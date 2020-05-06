node(n1).
node(n2).
node(n3).
node(n4).
node(n5).
node(n6).
node(n7).

left(n1, n2).
left(n2, n4).
left(n3, null).
left(n4, null).
left(n5, n6).
left(n6, null).
left(n7, null).

right(n1, n3).
right(n2, null).
right(n3, n5).
right(n4, null).
right(n5, n7).
right(n6, null).
right(n7, null).

entrypoint(n1).