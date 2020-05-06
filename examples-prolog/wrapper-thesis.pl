node(wrapper).
alpha(wrapper, s1).
bravo(wrapper, c1).

node(s1).
node(s2).

next(s1, s2).
next(s2, null).

node(c1).
node(c2).

next(c1, c2).
next(c2, c1).

entrypoint(wrapper).