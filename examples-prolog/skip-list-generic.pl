node(p1).
node(p2).
node(p3).

node(c1).
node(c2).
node(c3).
node(c4).

nextp(p1, p2).
nextp(p2, p3).
nextp(p3, null).

child(p1, c1).
child(p2, c2).
child(p3, c4).

next(c1, c2).
next(c2, c3).
next(c3, c4).
next(c4, null).

entrypoint(p1).