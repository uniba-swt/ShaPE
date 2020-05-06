node(t1s1).
node(t1s2).
node(t1s3).

next(t1s1, t1s2).
next(t1s2, t1s3).
next(t1s3, null).

entrypoint(t1s1).

node(t1n1).
node(t1n2).
node(t1n3).
node(t1n4).
node(t1n5).

left(t1n1, t1n2).
left(t1n2, t1n4).
left(t1n3, null).
left(t1n4, null).
left(t1n5, null).

right(t1n1, t1n3).
right(t1n2, null).
right(t1n3, t1n5).
right(t1n4, null).
right(t1n5, null).

entrypoint(t1n1).