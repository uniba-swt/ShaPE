% This example encodes the graph on the ShaPE logo when the lette "a" is
% considered a node instead of an entry pointer. The shape is known as a
% "lasso", i.e., the concatenation of an acyclic and a cyclic list segment.
% Interestingly, this version of a lasso can be described whereas lassos of
% arbitary size cannot (adequatly) be described. 

node(n1).
node(n2).
node(n3).
node(n4).
node(n5).
node(n6).

next(n1, n2).
next(n2, n3).
next(n3, n4).
next(n4, n5).
next(n5, n6).
next(n6, n2).

entrypoint(n1).