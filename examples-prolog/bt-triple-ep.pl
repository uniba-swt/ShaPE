node(root).
node(left).
node(right).
node(n4).
node(n5).

left(root, left).
left(left, n4).
left(right, null).
left(n4, null).
left(n5, null).

right(root, right).
right(left, null).
right(right, n5).
right(n4, null).
right(n5, null).

entrypoint(root).
entrypoint(left).
entrypoint(right).