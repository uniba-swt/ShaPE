node(p1).
node(p2).
node(p3).
node(p4).

next(p1, p2).
next(p2, p3).
next(p3, p4).
next(p4, null).

child(p1, c11).
child(p2, c21).
child(p3, c31).
child(p4, c41).

node(c11).
node(c21).
node(c22).
node(c31).
node(c32).
node(c41).
node(c42).
node(c43).

left(c11, null).
right(c11, null).

left(c21, c22).
right(c21, null).

left(c22, null).
right(c22, null).

left(c31, null).
right(c31, c32).

left(c32, null).
right(c32, null).

left(c41, c42).
right(c41, c43).

left(c42, null).
right(c42, null).

left(c43, null).
right(c43, null).


entrypoint(p1).