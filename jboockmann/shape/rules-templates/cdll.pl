entry(This) :- node(This), next(This, Next), prev(This, Prev), p(Next, This, Prev, This), true.
p(This, P1, P2, P1) :- node(This), next(This, Next), prev(This, P1), p(Next, This, P2, P1), true.
p(This, P1, P2, P3) :- node(This), next(This, Next), prev(This, P1), p(Next, This, P2, P3), true.
p(This, P1, P2, P3) :- node(This), next(This, P2), prev(This, P1), true, p(P2, This, P2, P3), true.
p(This, P1, This, P3) :- node(This), next(This, P3), prev(This, P1), true, true.

% the predicate is not strict enough, because it does not validate that prev of entry is indeed equal to the node whose next points to entry.
% entry(This) :- node(This), next(This, Next), prev(This, Prev), p(Next, This, This), true.
% p(This, P1, P2) :- node(This), next(This, P2), prev(This, P1), true.
% p(This, P1, P2) :- node(This), next(This, Next), prev(This, P1), p(Next, This, P2), true.