node(t1s1).
node(t1s2).

next(t1s1, t1s2).
next(t1s2, null).

entrypoint(t1s1).

node(t1n1).
node(t1n2).
node(t1n3).
node(t1n4).

left(t1n1, t1n2).
left(t1n2, t1n4).
left(t1n3, null).
left(t1n4, null).

right(t1n1, t1n3).
right(t1n2, null).
right(t1n3, null).
right(t1n4, null).

entrypoint(t1n1).