% Idea: create a ternary tree with left, mid, and right pointer

node(n1).
node(n2).
node(n3).
node(n4).

left(n1, n2).
left(n2, null).
left(n3, null).
left(n4, null).

mid(n1, n3).
mid(n2, null).
mid(n3, null).
mid(n4, null).

right(n1, n4).
right(n2, null).
right(n3, null).
right(n4, null).

entrypoint(n1).