entry(This) :- node(This), left(This, Left), right(This, Right), parent(This, null), p(Left, This), p(Right, This), true.
p(This, P1) :- node(This), left(This, null), right(This, null), parent(This, P1), true.
p(This, P1) :- node(This), left(This, null), right(This, Right), parent(This, P1), p(Right, This), true.
p(This, P1) :- node(This), left(This, Left), right(This, null), parent(This, P1), p(Left, This), true.
p(This, P1) :- node(This), left(This, Left), right(This, Right), parent(This, P1), p(Left, This), p(Right, This), true.