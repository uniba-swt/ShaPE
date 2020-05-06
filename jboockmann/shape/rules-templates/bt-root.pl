entry(This) :- node(This), left(This, Left), right(This, Right), p(Left, This), p(Right, This), true.
p(This, P1) :- node(This), left(This, P1), right(This, P1), true.
p(This, P1) :- node(This), left(This, P1), right(This, Right), p(Right, P1), true.
p(This, P1) :- node(This), left(This, Left), right(This, P1), p(Left, P1), true.
p(This, P1) :- node(This), left(This, Left), right(This, Right), p(Left, P1), p(Right, P1), true.