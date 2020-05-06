entry(This) :- node(This), left(This, Left), right(This, Right), root(This, This), p(Left, This), p(Right, This), true.
p(This, P1) :- node(This), left(This, null), right(This, null), root(This, P1), true.
p(This, P1) :- node(This), left(This, null), right(This, Right), root(This, P1), p(Right, P1), true.
p(This, P1) :- node(This), left(This, Left), right(This, null), root(This, P1), p(Left, P1), true.
p(This, P1) :- node(This), left(This, Left), right(This, Right), root(This, P1), p(Left, P1), p(Right, P1), true.