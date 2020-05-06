node(n12).
node(n19).
node(n32).

node(n8).
head(n8, n12).

next(n12, n19).
next(n19, n32).
next(n32, n12).

prev(n12, n32).
prev(n19, n12).
prev(n32, n19).

entrypoint(n8).